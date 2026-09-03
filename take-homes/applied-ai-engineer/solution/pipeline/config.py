"""Central, env-driven configuration (12-factor: config lives in the
environment, not hardcoded). Every path/tunable has a sensible default so
the pipeline runs out of the box against this repo's own `transcripts/` and
`data/` folders; overriding any of them (e.g. to point at a different
transcripts directory, or run the eval against a scratch state file so it
never touches the real ledger) is a single env var, no code change.

The one real secret, `OPENAI_API_KEY`, is read directly by llm_judge.py at
the point of use and is never stored on this Config object, logged, or
written to disk -- keeping it out of state_store.py's ledger and
logging_utils.py's event stream is deliberate.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .dedup import DEFAULT_SIMILARITY_THRESHOLD

# applied-ai-engineer/ (parent of solution/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_STATE_DIR = REPO_ROOT / "solution" / "state"


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser() if raw else default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    transcripts_dir: Path
    existing_issues_path: Path
    dev_labels_path: Path
    state_path: Path
    review_queue_path: Path
    review_decisions_path: Path
    log_path: Path
    similarity_threshold: float
    judge: str  # "heuristic" | "llm"
    openai_model: str


def load_config() -> Config:
    """Read Config from the environment. Safe to call repeatedly (e.g. once
    per CLI invocation); does not cache, so tests can freely monkeypatch
    os.environ between calls."""
    judge = os.environ.get("PIPELINE_JUDGE", "heuristic").strip().lower()
    if judge not in ("heuristic", "llm"):
        raise ValueError(f"PIPELINE_JUDGE must be 'heuristic' or 'llm', got {judge!r}")
    if judge == "llm" and not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("PIPELINE_JUDGE=llm requires OPENAI_API_KEY to be set")

    return Config(
        transcripts_dir=_env_path("PIPELINE_TRANSCRIPTS_DIR", REPO_ROOT / "transcripts"),
        existing_issues_path=_env_path(
            "PIPELINE_EXISTING_ISSUES", REPO_ROOT / "data" / "existing_issues.json"
        ),
        dev_labels_path=_env_path("PIPELINE_DEV_LABELS", REPO_ROOT / "data" / "dev_labels.json"),
        state_path=_env_path("PIPELINE_STATE_PATH", _STATE_DIR / "pipeline_state.json"),
        review_queue_path=_env_path("PIPELINE_REVIEW_QUEUE", _STATE_DIR / "review_queue.md"),
        review_decisions_path=_env_path(
            "PIPELINE_REVIEW_DECISIONS", _STATE_DIR / "review_decisions.json"
        ),
        log_path=_env_path("PIPELINE_LOG_PATH", _STATE_DIR / "events.jsonl"),
        similarity_threshold=_env_float(
            "PIPELINE_SIMILARITY_THRESHOLD", DEFAULT_SIMILARITY_THRESHOLD
        ),
        judge=judge,
        openai_model=os.environ.get("PIPELINE_OPENAI_MODEL", "gpt-4o-mini"),
    )
