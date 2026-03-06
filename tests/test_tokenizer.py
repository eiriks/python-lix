"""Tests for the tokenizer module."""

from __future__ import annotations

from lix.tokenizer import count_long_words, extract_words, split_sentences


class TestSplitSentences:
    """Tests for sentence boundary detection."""

    def test_simple_period(self) -> None:
        text = "Hei på deg. Hvordan har du det?"
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 2

    def test_multiple_punctuation_types(self) -> None:
        text = "Er du klar? Ja! Det er bra."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 3

    def test_abbreviation_not_split_nb(self) -> None:
        text = "Vi hadde bl.a. melk og brød. Det var fint."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 2

    def test_abbreviation_not_split_sv(self) -> None:
        text = "Vi hade t.ex. mjölk och bröd. Det var bra."
        sentences = split_sentences(text, "sv")
        assert len(sentences) == 2

    def test_abbreviation_not_split_da(self) -> None:
        text = "Vi havde f.eks. mælk og brød. Det var fint."
        sentences = split_sentences(text, "da")
        assert len(sentences) == 2

    def test_empty_text(self) -> None:
        assert split_sentences("", "nb") == []

    def test_whitespace_only(self) -> None:
        assert split_sentences("   ", "nb") == []

    def test_single_sentence(self) -> None:
        sentences = split_sentences("Hei på deg.", "nb")
        assert len(sentences) == 1

    def test_exclamation_and_question(self) -> None:
        text = "Hva skjer! Ingenting? Ok."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 3

    def test_scandinavian_uppercase_after_period(self) -> None:
        text = "Det er bra. Ål er godt. Ørnen flyr."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 3


class TestExtractWords:
    """Tests for word extraction."""

    def test_simple_words(self) -> None:
        words = extract_words("Hei på deg")
        assert words == ["Hei", "på", "deg"]

    def test_strips_punctuation(self) -> None:
        words = extract_words("Hei, verden! Hvordan går det?")
        assert "Hei" in words
        assert "verden" in words
        assert "," not in words
        assert "!" not in words

    def test_empty_string(self) -> None:
        assert extract_words("") == []

    def test_preserves_scandinavian_chars(self) -> None:
        words = extract_words("Ærlig talt, ørnen flyr over åsen")
        assert "Ærlig" in words
        assert "ørnen" in words
        assert "åsen" in words

    def test_hyphenated_word(self) -> None:
        words = extract_words("første-hjelpsutstyr er viktig")
        assert "første-hjelpsutstyr" in words

    def test_numbers_excluded(self) -> None:
        words = extract_words("Det var 42 studenter der.")
        assert "42" not in words


class TestCountLongWords:
    """Tests for long word counting."""

    def test_no_long_words(self) -> None:
        words = ["Hei", "på", "deg"]
        assert count_long_words(words) == 0

    def test_threshold_boundary(self) -> None:
        # 6 chars = NOT long, 7 chars = long
        assert count_long_words(["abcdef"]) == 0  # exactly 6
        assert count_long_words(["abcdefg"]) == 1  # exactly 7

    def test_mixed(self) -> None:
        words = ["kort", "mellomlangt", "veldig", "superlang"]
        # "mellomlangt" = 11, "superlang" = 9 → 2 long words
        # "veldig" = 6 → not long
        assert count_long_words(words) == 2

    def test_empty_list(self) -> None:
        assert count_long_words([]) == 0

    def test_scandinavian_compounds(self) -> None:
        words = ["stortingsrepresentanten", "diskuterte", "grunnlovsforslaget"]
        # All > 6 chars
        assert count_long_words(words) == 3


class TestSplitSentencesEdgeCases:
    """Additional edge cases for sentence boundary detection."""

    def test_ellipsis_splits_correctly(self) -> None:
        """ASCII ellipsis (...) should be treated as sentence boundary."""
        text = "Han sa at... Det var rart."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 2

    def test_unicode_ellipsis_no_split(self) -> None:
        """Unicode ellipsis (\u2026) is not a sentence boundary (expected behavior)."""
        text = "Han sa at\u2026 Det var rart."
        sentences = split_sentences(text, "nb")
        # Unicode ellipsis is not matched by [.!?], so treated as one sentence
        assert len(sentences) == 1

    def test_ordinal_number_not_split(self) -> None:
        """Period after a number (e.g. '1.') should not trigger a split."""
        text = "Han fikk 1. plass i konkurransen."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 1

    def test_multiple_abbreviations_in_one_sentence_nb(self) -> None:
        """Multiple abbreviations (bl.a., osv.) in a single sentence."""
        text = "Han kj\u00f8pte bl.a. melk, ost osv. fra butikken."
        sentences = split_sentences(text, "nb")
        assert len(sentences) == 1

    def test_nynorsk_abbreviation_td(self) -> None:
        """Nynorsk 't.d.' abbreviation should not split."""
        text = "Vi hadde t.d. mj\u00f8lk og br\u00f8d. Det var fint."
        sentences = split_sentences(text, "nn")
        assert len(sentences) == 2

    def test_swedish_from_tom_abbreviations(self) -> None:
        """Swedish 'fr.o.m.' and 't.o.m.' abbreviations should not split."""
        text = "Butiken har öppet fr.o.m. måndag t.o.m. fredag. Det är bra."
        sentences = split_sentences(text, "sv")
        assert len(sentences) == 2

    def test_text_without_period_is_one_sentence(self) -> None:
        """Text with no sentence-ending punctuation is treated as one sentence."""
        sentences = split_sentences("dette er bare tekst uten punktum", "nb")
        assert len(sentences) == 1

    def test_only_punctuation(self) -> None:
        """A lone period should return as a single sentence element."""
        sentences = split_sentences(".", "nb")
        assert len(sentences) == 1


class TestExtractWordsEdgeCases:
    """Additional edge cases for word extraction."""

    def test_only_numbers_returns_empty(self) -> None:
        """Pure numeric text has no alpha words."""
        assert extract_words("123 456 789") == []

    def test_mixed_numbers_and_words(self) -> None:
        """Numbers are excluded, alpha words are kept."""
        words = extract_words("Det var 42 katter og 7 hunder.")
        assert "42" not in words
        assert "7" not in words
        assert "katter" in words
        assert "hunder" in words

    def test_leading_trailing_hyphens_stripped(self) -> None:
        """Hyphens at start/end of a token are stripped."""
        words = extract_words("-test- er -viktig-")
        assert "test" in words
        assert "viktig" in words
        # No leading/trailing hyphen tokens
        assert all(not w.startswith("-") and not w.endswith("-") for w in words)
