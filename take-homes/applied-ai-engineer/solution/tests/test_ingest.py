"""Unit tests for ingest.py -- transcript parsing, path ordering, and the
internal-owner-name heuristic used for Slack routing.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from solution.pipeline.ingest import (
    TranscriptParseError,
    internal_owner_name,
    iter_transcript_paths,
    load_transcripts,
    parse_transcript,
)
from solution.pipeline.models import Speaker


def _write(directory: Path, filename: str, text: str) -> Path:
    path = directory / filename
    path.write_text(text, encoding="utf-8")
    return path


_WELL_FORMED = """# Call \u2014 Acme Corp \u00d7 BetterBark \u00b7 Support
Date: 2026-06-17 \u00b7 Call ID: call-003
Participants: [EXTERNAL] Renee Park, IT Security Lead (Atlas Financial) \u00b7 [INTERNAL] Tom\u00e1s Vela, Implementation

[EXTERNAL] Renee: The export button is broken.
[INTERNAL] Tomas: Can you tell me more?
[EXTERNAL] Renee: It just returns a blank file
every single time.
"""


class TestParseTranscript(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_happy_path_fields(self) -> None:
        path = _write(self.dir, "call-003.md", _WELL_FORMED)
        t = parse_transcript(path)
        self.assertEqual(t.call_id, "call-003")
        self.assertEqual(t.date, "2026-06-17")
        self.assertEqual(t.account, "Acme Corp")
        self.assertEqual(t.call_type, "Support")
        self.assertIn("[INTERNAL] Tom\u00e1s Vela", t.participants_raw)
        self.assertEqual(t.path, str(path))

    def test_turns_parsed_with_correct_speaker_and_sequential_index(self) -> None:
        path = _write(self.dir, "call-003.md", _WELL_FORMED)
        t = parse_transcript(path)
        self.assertEqual(len(t.turns), 3)
        self.assertEqual(t.turns[0].speaker, Speaker.EXTERNAL)
        self.assertEqual(t.turns[0].name, "Renee")
        self.assertEqual(t.turns[1].speaker, Speaker.INTERNAL)
        self.assertEqual([turn.index for turn in t.turns], [0, 1, 2])

    def test_continuation_line_appended_to_previous_turn(self) -> None:
        path = _write(self.dir, "call-003.md", _WELL_FORMED)
        t = parse_transcript(path)
        self.assertEqual(t.turns[2].text, "It just returns a blank file every single time.")

    def test_title_without_betterbark_marker_has_no_account(self) -> None:
        text = _WELL_FORMED.replace("Acme Corp \u00d7 BetterBark \u00b7 Support", "Internal Sync")
        path = _write(self.dir, "call-003.md", text)
        t = parse_transcript(path)
        self.assertIsNone(t.account)
        self.assertEqual(t.call_type, "Internal Sync")

    def test_missing_title_header_raises(self) -> None:
        text = _WELL_FORMED.replace("# Call \u2014 Acme Corp \u00d7 BetterBark \u00b7 Support\n", "")
        path = _write(self.dir, "call-003.md", text)
        with self.assertRaises(TranscriptParseError):
            parse_transcript(path)

    def test_missing_date_header_raises(self) -> None:
        text = _WELL_FORMED.replace("Date: 2026-06-17 \u00b7 Call ID: call-003\n", "")
        path = _write(self.dir, "call-003.md", text)
        with self.assertRaises(TranscriptParseError):
            parse_transcript(path)

    def test_no_dialogue_turns_raises(self) -> None:
        text = "# Call \u2014 Acme Corp \u00d7 BetterBark \u00b7 Support\nDate: 2026-06-17 \u00b7 Call ID: call-003\n"
        path = _write(self.dir, "call-003.md", text)
        with self.assertRaises(TranscriptParseError):
            parse_transcript(path)

    def test_has_external_participant_true_when_external_turns_present(self) -> None:
        path = _write(self.dir, "call-003.md", _WELL_FORMED)
        t = parse_transcript(path)
        self.assertTrue(t.has_external_participant)
        self.assertEqual(len(t.external_turns()), 2)


class TestIterTranscriptPaths(unittest.TestCase):
    def test_sorts_numerically_not_lexicographically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name in ("call-2.md", "call-10.md", "call-1.md"):
                _write(directory, name, _WELL_FORMED)
            paths = iter_transcript_paths(directory)
            self.assertEqual([p.name for p in paths], ["call-1.md", "call-2.md", "call-10.md"])


class TestLoadTranscripts(unittest.TestCase):
    def test_fails_fast_on_first_bad_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "call-1.md", _WELL_FORMED)
            _write(directory, "call-2.md", "not a valid transcript\n")
            with self.assertRaises(TranscriptParseError):
                load_transcripts(directory)


class TestInternalOwnerName(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_extracts_name_from_participants_raw(self) -> None:
        path = _write(self.dir, "call-003.md", _WELL_FORMED)
        t = parse_transcript(path)
        self.assertEqual(internal_owner_name(t), "Tom\u00e1s Vela")

    def test_falls_back_to_first_internal_turn_name(self) -> None:
        text = _WELL_FORMED.replace(
            "Participants: [EXTERNAL] Renee Park, IT Security Lead (Atlas Financial) \u00b7 [INTERNAL] Tom\u00e1s Vela, Implementation\n",
            "Participants: [EXTERNAL] Renee Park, IT Security Lead (Atlas Financial)\n",
        )
        path = _write(self.dir, "call-003.md", text)
        t = parse_transcript(path)
        self.assertEqual(internal_owner_name(t), "Tomas")  # first [INTERNAL] turn's speaker name

    def test_falls_back_to_unknown_owner_when_nothing_available(self) -> None:
        text = (
            "# Call \u2014 Acme Corp \u00d7 BetterBark \u00b7 Support\n"
            "Date: 2026-06-17 \u00b7 Call ID: call-003\n"
            "Participants: none on file\n\n"
            "[EXTERNAL] Renee: Hello, anyone there?\n"
        )
        path = _write(self.dir, "call-003.md", text)
        t = parse_transcript(path)
        self.assertEqual(internal_owner_name(t), "unknown-owner")


if __name__ == "__main__":
    unittest.main()
