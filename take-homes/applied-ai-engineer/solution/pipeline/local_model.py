from __future__ import annotations

from pathlib import Path
from time import monotonic
import argparse
import hashlib
import json

from .llm_judge import LLMJudgeError

MODEL_REPOSITORY = "jncraton/Qwen3-4B-Instruct-2507-ct2-int8"
MODEL_REVISION = "ab26c167dd687295980bbfc9f6b696f455b794c4"
MODEL_SHA256 = "4307805dc2a0f2b7a10e2d514e4627db153924ad2d4a808dc9a3ea593c1d2083"
OV_REPOSITORY = "OpenVINO/Qwen3.5-4B-int4-ov"
OV_REVISION = "f2377291372c62c0114ee20a094261fa3b193b0b"
OV_LARGE_REPOSITORY = "OpenVINO/Qwen3.5-9B-int4-ov"
OV_LARGE_REVISION = "ee5a3761d4524966dd6c1f1037694ebc581cb196"
OV_LARGE_HASHES = {
    "openvino_language_model.bin": "2bb128ebf0844652bfa0155e16d76669c1235b2f4060ecd246fdfb9e6c530427",
    "openvino_text_embeddings_model.bin": "fd80debc3c239af673f7dd2571e860b4a47dee2e4ef52b458fdfdef4195dfd06",
}
OV_HASHES = {
    "openvino_language_model.bin": "57032d8f7c75fa02310d9bde2bcd484c5889e2f12b1dda9856f40c9f10de5476",
    "openvino_text_embeddings_model.bin": "b2151262ea17cb43e4cb745e6317eeb8208752e3d13c3d719e1fcfa1e704e505",
    "tokenizer.json": "87a7830d63fcf43bf241c3c5242e96e62dd3fdc29224ca26fed8ea333db72de4",
}


def download_model(engine: str = "ctranslate2", size: str = "4b") -> Path:
    from huggingface_hub import snapshot_download

    if size not in ("4b", "9b") or (size == "9b" and engine != "openvino"):
        raise ValueError("Unsupported local model size/engine combination")
    if engine == "openvino" and size == "9b":
        directory = Path(snapshot_download(OV_LARGE_REPOSITORY, revision=OV_LARGE_REVISION,
                                           allow_patterns=["*.bin", "*.xml", "*.json", "*.jinja"]))
        hashes = OV_LARGE_HASHES
    elif engine == "openvino":
        directory = Path(snapshot_download(OV_REPOSITORY, revision=OV_REVISION,
                                           allow_patterns=["*.bin", "*.xml", "*.json", "*.jinja"]))
        hashes = OV_HASHES
    elif engine == "ctranslate2":
        directory = Path(snapshot_download(MODEL_REPOSITORY, revision=MODEL_REVISION,
                                           allow_patterns=["model.bin", "*.json"]))
        hashes = {"model.bin": MODEL_SHA256}
    else:
        raise ValueError("Unknown local inference engine")
    for filename, expected in hashes.items():
        with (directory / filename).open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Downloaded {filename} checksum differs from pinned publisher metadata")
    return directory


def render_qwen_chat(messages: list[dict]) -> str:
    parts = []
    for message in messages:
        role = message["role"]
        if role not in ("system", "user"):
            raise ValueError("Local extraction accepts only system and user messages")
        content = message["content"].replace("<|", "< |").replace("|>", "| >")
        parts.append(f"<|im_start|>{role}\n{content}<|im_end|>\n")
    return "".join(parts) + "<|im_start|>assistant\n"


class QwenCT2Transport:
    def __init__(self, model_path: Path, *, generator=None, tokenizer=None,
                 max_input_tokens: int = 12000, max_output_tokens: int = 2048,
                 timeout_seconds: float = 300, threads: int = 8,
                 report_progress: bool = False) -> None:
        if generator is None:
            import ctranslate2

            generator = ctranslate2.Generator(str(model_path), device="cpu", compute_type="int8",
                                              intra_threads=threads, inter_threads=1)
        if tokenizer is None:
            from tokenizers import Tokenizer

            tokenizer = Tokenizer.from_file(str(Path(model_path) / "tokenizer.json"))
        self.generator = generator
        self.tokenizer = tokenizer
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds
        self.report_progress = report_progress

    def __call__(self, api_key: str, payload: dict) -> dict:
        encoded = self.tokenizer.encode(render_qwen_chat(payload["messages"]), add_special_tokens=False)
        if len(encoded.tokens) > self.max_input_tokens:
            raise LLMJudgeError("Transcript exceeds local context budget; refusing silent truncation")
        maximum = min(payload.get("max_tokens", self.max_output_tokens), self.max_output_tokens)
        started = monotonic()
        timed_out = False

        def deadline(step) -> bool:
            nonlocal timed_out
            timed_out = monotonic() - started > self.timeout_seconds
            return timed_out

        result = self.generator.generate_batch(
            [encoded.tokens], max_length=maximum, sampling_topk=1, beam_size=1,
            include_prompt_in_result=False, end_token=["<|im_end|>", "<|endoftext|>"],
            return_end_token=True, callback=deadline,
        )[0]
        if timed_out:
            raise LLMJudgeError("Local generation exceeded its time budget")
        token_ids = result.sequences_ids[0]
        end_ids = {self.tokenizer.token_to_id(token) for token in ("<|im_end|>", "<|endoftext|>")}
        finished = bool(token_ids and token_ids[-1] in end_ids)
        content = self.tokenizer.decode(token_ids, skip_special_tokens=True)
        if self.report_progress:
            print(json.dumps({"event": "local_inference_completed", "elapsed_seconds": round(monotonic() - started, 3),
                              "prompt_tokens": len(encoded.tokens), "completion_tokens": len(token_ids),
                              "finished": finished}), flush=True)
        return {"choices": [{"message": {"content": content}, "finish_reason": "stop" if finished else "length"}],
                "usage": {"prompt_tokens": len(encoded.tokens), "completion_tokens": len(token_ids)}}


class QwenOpenVINOTransport:
    def __init__(self, model_path: Path, *, pipeline=None, tokenizer=None,
                 device: str = "GPU", timeout_seconds: float = 180,
                 max_input_tokens: int = 12000, max_output_tokens: int = 2048,
                 report_progress: bool = False) -> None:
        if pipeline is None:
            import openvino_genai

            pipeline = openvino_genai.VLMPipeline(str(model_path), device)
        if tokenizer is None:
            from tokenizers import Tokenizer

            tokenizer = Tokenizer.from_file(str(Path(model_path) / "tokenizer.json"))
        self.pipeline = pipeline
        self.tokenizer = tokenizer
        self.timeout_seconds = timeout_seconds
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.report_progress = report_progress

    def __call__(self, api_key: str, payload: dict) -> dict:
        prompt = render_qwen_chat(payload["messages"]) + "<think>\n\n</think>\n\n"
        if len(self.tokenizer.encode(prompt, add_special_tokens=False).tokens) > self.max_input_tokens:
            raise LLMJudgeError("Transcript exceeds local context budget; refusing silent truncation")
        maximum = min(payload.get("max_tokens", self.max_output_tokens), self.max_output_tokens)
        started = monotonic()
        timed_out = False

        def deadline(text) -> bool:
            nonlocal timed_out
            timed_out = monotonic() - started > self.timeout_seconds
            return timed_out

        result = self.pipeline.generate(prompt, max_new_tokens=maximum, do_sample=False,
                                        apply_chat_template=False, streamer=deadline)
        if timed_out:
            raise LLMJudgeError("Local generation exceeded its time budget")
        generated = result.perf_metrics.get_num_generated_tokens()
        finished = generated < maximum
        if self.report_progress:
            print(json.dumps({"event": "local_inference_completed", "engine": "openvino",
                              "elapsed_seconds": round(monotonic() - started, 3),
                              "prompt_tokens": result.perf_metrics.get_num_input_tokens(),
                              "completion_tokens": generated, "finished": finished}), flush=True)
        return {"choices": [{"message": {"content": result.texts[0]},
                              "finish_reason": "stop" if finished else "length"}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and verify the pinned free local instruction model.")
    parser.add_argument("command", choices=["download"])
    parser.add_argument("--engine", choices=["ctranslate2", "openvino"], default="ctranslate2")
    parser.add_argument("--size", choices=["4b", "9b"], default="4b")
    args = parser.parse_args()
    print(download_model(args.engine, args.size))