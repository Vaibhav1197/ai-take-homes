"""Unit tests for text_utils.py -- tokenization, number-word extraction, and
the from-scratch TF-IDF/cosine-similarity primitives dedup.py relies on.
"""
from __future__ import annotations

import unittest

from solution.pipeline.text_utils import (
    TfidfIndex,
    cosine_similarity,
    extract_max_impact_count,
    find_matches,
    jaccard_similarity,
    normalize_whitespace,
    significant_tokens,
    tokenize,
)


class TestNormalizeWhitespace(unittest.TestCase):
    def test_collapses_internal_whitespace_and_strips_ends(self) -> None:
        self.assertEqual(normalize_whitespace("  a   b\tc\n d  "), "a b c d")


class TestTokenize(unittest.TestCase):
    def test_lowercases_and_splits_on_non_alnum(self) -> None:
        self.assertEqual(tokenize("Export API's are Broken!"), ["export", "api", "s", "are", "broken"])

    def test_empty_string_yields_no_tokens(self) -> None:
        self.assertEqual(tokenize(""), [])


class TestSignificantTokens(unittest.TestCase):
    def test_filters_stopwords_and_short_tokens(self) -> None:
        tokens = significant_tokens("the export is broken and it is a bug")
        self.assertNotIn("the", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("it", tokens)
        self.assertIn("export", tokens)
        self.assertIn("broken", tokens)
        self.assertIn("bug", tokens)


class TestFindMatches(unittest.TestCase):
    def test_returns_only_phrases_present_in_text(self) -> None:
        hits = find_matches("the export button is broken", ("broken", "wrong", "export"))
        self.assertEqual(set(hits), {"broken", "export"})

    def test_no_matches_returns_empty_list(self) -> None:
        self.assertEqual(find_matches("everything is fine", ("broken", "wrong")), [])


class TestExtractMaxImpactCount(unittest.TestCase):
    def test_digit_form(self) -> None:
        self.assertEqual(extract_max_impact_count("we have 31 members affected"), 31)

    def test_word_form_simple(self) -> None:
        self.assertEqual(extract_max_impact_count("about twenty users hit this"), 20)

    def test_word_form_compound(self) -> None:
        self.assertEqual(extract_max_impact_count("roughly sixty seven drivers saw it"), 67)

    def test_hundred_composition(self) -> None:
        self.assertEqual(extract_max_impact_count("two hundred employees affected"), 200)

    def test_thousand_composition(self) -> None:
        self.assertEqual(extract_max_impact_count("two thousand accounts impacted"), 2000)

    def test_dozen_word(self) -> None:
        self.assertEqual(extract_max_impact_count("a dozen customers called in"), 12)

    def test_no_impact_phrase_returns_none(self) -> None:
        self.assertIsNone(extract_max_impact_count("the export button is broken"))

    def test_picks_the_maximum_when_multiple_mentioned(self) -> None:
        text = "it started with 5 users but now it's up to 200 members affected"
        self.assertEqual(extract_max_impact_count(text), 200)


class TestJaccardSimilarity(unittest.TestCase):
    def test_identical_sets_score_one(self) -> None:
        self.assertEqual(jaccard_similarity({"a", "b"}, {"a", "b"}), 1.0)

    def test_disjoint_sets_score_zero(self) -> None:
        self.assertEqual(jaccard_similarity({"a"}, {"b"}), 0.0)

    def test_empty_input_scores_zero(self) -> None:
        self.assertEqual(jaccard_similarity(set(), {"a"}), 0.0)
        self.assertEqual(jaccard_similarity({"a"}, set()), 0.0)

    def test_partial_overlap(self) -> None:
        self.assertAlmostEqual(jaccard_similarity({"a", "b"}, {"b", "c"}), 1 / 3)


class TestCosineSimilarity(unittest.TestCase):
    def test_identical_vectors_score_one(self) -> None:
        v = {"a": 2.0, "b": 1.0}
        self.assertAlmostEqual(cosine_similarity(v, v), 1.0)

    def test_orthogonal_vectors_score_zero(self) -> None:
        self.assertEqual(cosine_similarity({"a": 1.0}, {"b": 1.0}), 0.0)

    def test_empty_vector_scores_zero(self) -> None:
        self.assertEqual(cosine_similarity({}, {"a": 1.0}), 0.0)
        self.assertEqual(cosine_similarity({"a": 1.0}, {}), 0.0)


class TestTfidfIndex(unittest.TestCase):
    def test_empty_corpus_best_match_is_none(self) -> None:
        index = TfidfIndex([])
        idx, sim = index.best_match("anything at all")
        self.assertIsNone(idx)
        self.assertEqual(sim, 0.0)

    def test_identical_document_scores_highest(self) -> None:
        index = TfidfIndex([
            "search results are stale after a member rename",
            "export button returns a blank csv file",
        ])
        idx, sim = index.best_match("export button returns a blank csv file")
        self.assertEqual(idx, 1)
        self.assertGreater(sim, 0.5)

    def test_unrelated_query_scores_low(self) -> None:
        index = TfidfIndex(["search results are stale after a member rename"])
        _, sim = index.best_match("completely unrelated pricing and contract renewal discussion")
        self.assertLess(sim, 0.2)

    def test_add_document_grows_corpus_for_future_queries(self) -> None:
        index = TfidfIndex(["search results are stale after a member rename"])
        new_idx = index.add_document("export button returns a blank csv file")
        self.assertEqual(new_idx, 1)
        idx, sim = index.best_match("export button returns a blank csv file")
        self.assertEqual(idx, 1)
        self.assertGreater(sim, 0.5)


if __name__ == "__main__":
    unittest.main()
