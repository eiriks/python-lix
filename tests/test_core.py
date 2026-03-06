"""Tests for the core readability computation module."""

from __future__ import annotations

import pytest

from lix import Difficulty, ReadabilityResult, compute, compute_lix, compute_rix


class TestComputeLix:
    """Tests for the LIX score computation."""

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            compute_lix("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            compute_lix("   ")

    def test_no_sentence_ending_treated_as_one(self) -> None:
        # Text without .!? is treated as a single sentence
        score = compute_lix("hei på deg")
        assert isinstance(score, float)

    def test_simple_text_score(self, simple_norwegian_text: str) -> None:
        score = compute_lix(simple_norwegian_text)
        # Simple text with short words should have a low LIX
        assert score < 30

    def test_complex_text_higher_score(self, complex_norwegian_text: str) -> None:
        score = compute_lix(complex_norwegian_text)
        # Complex text with long compound words should score higher
        assert score > 40

    def test_known_score(self) -> None:
        # "Hunden er stor. Katten er liten."
        # 6 words, 2 sentences → avg sentence length = 3
        # No long words (all ≤ 6 chars) → long word % = 0
        # LIX = 3 + 0 = 3.0
        text = "Hunden er stor. Katten er liten."
        score = compute_lix(text)
        assert score == pytest.approx(3.0, abs=0.1)

    def test_language_parameter_accepted(self) -> None:
        text = "Hunden er stor. Katten er liten."
        # Should work for all supported languages
        for lang in ("nb", "nn", "da", "sv", "en"):
            score = compute_lix(text, language=lang)  # type: ignore[arg-type]
            assert isinstance(score, float)


class TestComputeRix:
    """Tests for the RIX score computation."""

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            compute_rix("")

    def test_no_long_words_gives_zero(self) -> None:
        # All words ≤ 6 chars
        text = "Hei på deg. Ha det."
        score = compute_rix(text)
        assert score == pytest.approx(0.0)

    def test_rix_formula_correct(self) -> None:
        # "Representanten diskuterte forslaget. Det var viktig."
        # Sentence 1 words: Representanten(15), diskuterte(10), forslaget(9) → 3 long
        # Sentence 2 words: Det(3), var(3), viktig(6) → 0 long
        # Total: 3 long words, 2 sentences → RIX = 3/2 = 1.5
        text = "Representanten diskuterte forslaget. Det var viktig."
        score = compute_rix(text)
        assert score == pytest.approx(1.5)

    def test_rix_increases_with_complexity(
        self,
        simple_norwegian_text: str,
        complex_norwegian_text: str,
    ) -> None:
        simple_rix = compute_rix(simple_norwegian_text)
        complex_rix = compute_rix(complex_norwegian_text)
        assert complex_rix > simple_rix


class TestCompute:
    """Tests for the combined compute function."""

    def test_returns_readability_result(self, simple_norwegian_text: str) -> None:
        result = compute(simple_norwegian_text)
        assert isinstance(result, ReadabilityResult)

    def test_result_fields_populated(self, simple_norwegian_text: str) -> None:
        result = compute(simple_norwegian_text)
        assert result.word_count > 0
        assert result.sentence_count > 0
        assert result.long_word_count >= 0
        assert result.language == "nb"
        assert isinstance(result.difficulty, Difficulty)

    def test_lix_and_rix_consistent(self, simple_norwegian_text: str) -> None:
        result = compute(simple_norwegian_text)
        standalone_lix = compute_lix(simple_norwegian_text)
        standalone_rix = compute_rix(simple_norwegian_text)
        assert result.lix == pytest.approx(standalone_lix)
        assert result.rix == pytest.approx(standalone_rix)

    def test_difficulty_very_easy(self) -> None:
        text = "Hei. Ja. Nei. Ok. Bra."
        result = compute(text)
        assert result.difficulty == Difficulty.VERY_EASY

    def test_difficulty_classification(self, complex_norwegian_text: str) -> None:
        result = compute(complex_norwegian_text)
        # Complex political text should be at least medium difficulty
        assert result.difficulty in (
            Difficulty.MEDIUM,
            Difficulty.HARD,
            Difficulty.VERY_HARD,
        )

    def test_danish_language(self, danish_text: str) -> None:
        result = compute(danish_text, language="da")
        assert result.language == "da"
        assert result.lix > 0

    def test_swedish_language(self, swedish_text: str) -> None:
        result = compute(swedish_text, language="sv")
        assert result.language == "sv"
        assert result.lix > 0

    def test_frozen_result(self, simple_norwegian_text: str) -> None:
        result = compute(simple_norwegian_text)
        with pytest.raises(AttributeError):
            result.lix = 999.0  # type: ignore[misc]


class TestClassifyLix:
    """Tests for LIX score classification."""

    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (10.0, Difficulty.VERY_EASY),
            (24.9, Difficulty.VERY_EASY),
            (25.0, Difficulty.EASY),
            (34.9, Difficulty.EASY),
            (35.0, Difficulty.MEDIUM),
            (44.9, Difficulty.MEDIUM),
            (45.0, Difficulty.HARD),
            (54.9, Difficulty.HARD),
            (55.0, Difficulty.VERY_HARD),
            (80.0, Difficulty.VERY_HARD),
        ],
    )
    def test_boundaries(self, score: float, expected: Difficulty) -> None:
        from lix import classify_lix

        assert classify_lix(score) == expected


class TestLixDifficultyBands:
    """Parametrized tests verifying LIX scores across the full difficulty spectrum.

    Each text is hand-calibrated with verified word/sentence/long-word counts."""

    @pytest.mark.parametrize(
        ("text", "language", "expected_lix", "expected_difficulty"),
        [
            # VERY_EASY (LIX < 25): 9 words, 3 sentences, 0 long words
            # LIX = 9/3 + 0 = 3.0
            (
                "Jeg er her. Du er der. Vi er to.",
                "nb",
                3.0,
                Difficulty.VERY_EASY,
            ),
            # EASY (25-34): 19 words, 1 sentence, 2 long words
            # oppgaven(8), resultat(8)
            # LIX = 19/1 + (2*100)/19 = 19 + 10.53 = 29.53
            (
                (
                    "Han jobbet lenge med den store oppgaven "
                    "og fikk til slutt et godt og viktig resultat til dem alle."
                ),
                "nb",
                29.53,
                Difficulty.EASY,
            ),
            # MEDIUM (35-44): 17 words, 2 sentences, 6 long words
            # LIX = 17/2 + (6*100)/17 = 8.5 + 35.29 = 43.79
            (
                (
                    "Forskerne har oppdaget et nytt materiale "
                    "som kan erstatte plast. "
                    "Materialet testes på et laboratorium i dag."
                ),
                "nb",
                43.79,
                Difficulty.MEDIUM,
            ),
            # HARD (45-54): 14 words, 2 sentences, 6 long words
            # LIX = 14/2 + (6*100)/14 = 7.0 + 42.86 = 49.86
            (
                (
                    "Ministeren drøftet de nye reglene. "
                    "Partene var stort sett enige om punktene i avtalen."
                ),
                "nb",
                49.86,
                Difficulty.HARD,
            ),
            # VERY_HARD (LIX > 55): 10 words, 1 sentence, 8 long words
            # mellom(6) and og(2) are short; rest are 7+ chars
            # LIX = 10/1 + (8*100)/10 = 10 + 80 = 90.0
            (
                (
                    "Grunnlovsbestemmelsene vedr\u00f8rende kommuneforvaltningens "
                    "organisasjonsstruktur diskuteres inng\u00e5ende mellom "
                    "stortingsrepresentantene og departementsr\u00e5dgiverne."
                ),
                "nb",
                90.0,
                Difficulty.VERY_HARD,
            ),
        ],
        ids=["very_easy", "easy", "medium", "hard", "very_hard"],
    )
    def test_lix_difficulty_band(
        self,
        text: str,
        language: str,
        expected_lix: float,
        expected_difficulty: Difficulty,
    ) -> None:
        result = compute(text, language=language)  # type: ignore[arg-type]
        assert result.lix == pytest.approx(expected_lix, abs=0.1)
        assert result.difficulty == expected_difficulty


class TestRixScaleBands:
    """Parametrized tests verifying RIX scores across the full RIX scale.

    RIX scale: <0.5 very easy, 0.5-1.1 easy, 1.1-2.1 medium,
    2.1-3.0 hard, >3.0 very hard."""

    @pytest.mark.parametrize(
        ("text", "expected_rix"),
        [
            # RIX = 0.0 (very easy): 0 long words, 3 sentences
            ("Hei på deg. Ha det bra. Vi ses.", 0.0),
            # RIX = 0.5 (easy): 1 long word (sentrum=7), 2 sentences
            (
                "Vi kan gå til sentrum og spise. Det er en fin dag i dag.",
                0.5,
            ),
            # RIX = 1.0 (easy): 1 long word (butikken=8), 1 sentence
            ("Han gikk til butikken for å kjøpe mat.", 1.0),
            # RIX = 1.5 (medium): 3 long words, 2 sentences
            # butikken(8), hyggelig(8), kvelden(7)
            (
                ("Han kjøpte melk i butikken i går. Det ble en hyggelig kvelden ute."),
                1.5,
            ),
            # RIX = 2.5 (hard): 5 long words, 2 sentences
            # besøkte(7), butikken(8), familien(8), hyggelig(8), kvelden(7)
            (
                (
                    "Vi har besøkte den store butikken med familien. "
                    "Det var en hyggelig kvelden for oss alle."
                ),
                2.5,
            ),
            # RIX = 4.0 (very hard): 4 long words, 1 sentence
            (
                (
                    "Stortingsrepresentanten diskuterte "
                    "grunnlovsforslaget i interpellasjonsdebattene."
                ),
                4.0,
            ),
        ],
        ids=[
            "very_easy_0.0",
            "easy_0.5",
            "easy_1.0",
            "medium_1.5",
            "hard_2.5",
            "very_hard_4.0",
        ],
    )
    def test_rix_scale_band(self, text: str, expected_rix: float) -> None:
        score = compute_rix(text)
        assert score == pytest.approx(expected_rix, abs=0.01)


class TestEdgeCases:
    """Edge case tests for error paths and unusual inputs."""

    def test_numbers_only_text_raises_no_words(self) -> None:
        """Text containing only numbers triggers 'No words detected' error."""
        with pytest.raises(ValueError, match="No words detected"):
            compute_lix("123 456.")

    def test_numbers_with_sentence_boundaries_raises(self) -> None:
        """Numbers with periods still fail when no alpha words are present."""
        with pytest.raises(ValueError, match="No words detected"):
            compute_rix("123. 456. 789.")

    def test_nynorsk_language(self) -> None:
        """Nynorsk (nn) language code produces valid results."""
        text = "Katten sat på matta. Ho var svart og lita."
        result = compute(text, language="nn")
        assert result.language == "nn"
        assert result.lix > 0
        assert result.rix >= 0

    def test_single_word_sentence(self) -> None:
        """A single-word sentence should still compute."""
        score = compute_lix("Hei.")
        assert score == pytest.approx(1.0, abs=0.1)

    def test_all_long_words(self) -> None:
        """Text where every word is long should have high long-word percentage."""
        text = "Stortingsrepresentanten diskuterte grunnlovsforslaget."
        result = compute(text)
        assert result.long_word_count == result.word_count
        assert result.lix > 100  # 3/1 + 300/3 = 103


class TestEnglishSupport:
    """Tests for English language support."""

    def test_simple_english_text(self, simple_english_text: str) -> None:
        score = compute_lix(simple_english_text, language="en")
        # Simple text with short words should have a low LIX
        assert score < 30

    def test_complex_english_higher_score(
        self,
        simple_english_text: str,
        complex_english_text: str,
    ) -> None:
        simple = compute_lix(simple_english_text, language="en")
        complex_ = compute_lix(complex_english_text, language="en")
        assert complex_ > simple

    def test_english_compute_returns_result(self, simple_english_text: str) -> None:
        result = compute(simple_english_text, language="en")
        assert isinstance(result, ReadabilityResult)
        assert result.language == "en"
        assert result.word_count > 0
        assert result.sentence_count > 0
        assert isinstance(result.difficulty, Difficulty)

    def test_english_known_score(self) -> None:
        # "The dog is big. The cat is small."
        # 8 words, 2 sentences → avg sentence length = 4
        # No long words (all ≤ 6 chars) → long word % = 0
        # LIX = 4 + 0 = 4.0
        text = "The dog is big. The cat is small."
        score = compute_lix(text, language="en")
        assert score == pytest.approx(4.0, abs=0.1)

    def test_english_rix(self, simple_english_text: str) -> None:
        score = compute_rix(simple_english_text, language="en")
        assert isinstance(score, float)
        assert score >= 0

    def test_english_complex_difficulty(self, complex_english_text: str) -> None:
        result = compute(complex_english_text, language="en")
        # Complex text with long words should be at least medium difficulty
        assert result.difficulty in (
            Difficulty.MEDIUM,
            Difficulty.HARD,
            Difficulty.VERY_HARD,
        )
