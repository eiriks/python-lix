"""Tests for the GEO (Generative Engine Optimization) analysis module."""

from __future__ import annotations

import pytest

from lix import GEOResult, analyze_geo


class TestAnalyzeGeoValidation:
    """Tests for input validation."""

    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            analyze_geo("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            analyze_geo("   ")

    def test_too_few_words_raises(self) -> None:
        with pytest.raises(ValueError, match="at least 3 words"):
            analyze_geo("Hi.")

    def test_no_sentence_boundary_not_raised_for_text_without_period(self) -> None:
        """Text without .!? is treated as a single sentence by the tokenizer."""
        result = analyze_geo("no punctuation here at all")
        assert result.sentence_count == 1

    def test_returns_geo_result(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert isinstance(result, GEOResult)

    def test_frozen_result(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        with pytest.raises(AttributeError):
            result.statistics_density = 999.0  # type: ignore[misc]


class TestStatisticsDensity:
    """Tests for statistics/data detection."""

    def test_percentage(self) -> None:
        result = analyze_geo("About 73% of users prefer this method. The rest do not.")
        assert result.statistics_density > 0

    def test_dollar_amount(self) -> None:
        result = analyze_geo("The project cost $1,000 to complete. It was worth it.")
        assert result.statistics_density > 0

    def test_euro_amount(self) -> None:
        result = analyze_geo("The budget was €500 for the entire trip. We saved money.")
        assert result.statistics_density > 0

    def test_multiplier_comparison(self) -> None:
        result = analyze_geo(
            "The new system is 3x faster than the old one. Users love it."
        )
        assert result.statistics_density > 0

    def test_large_number(self) -> None:
        result = analyze_geo(
            "The company earned 5 billion dollars last year. Revenue grew fast."
        )
        assert result.statistics_density > 0

    def test_no_statistics(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.statistics_density == pytest.approx(0.0)

    def test_multiple_stats_in_one_sentence(self) -> None:
        result = analyze_geo(
            "Revenue grew 15% to $2,000 last quarter. Growth was strong."
        )
        # Should detect both the percentage and dollar amount
        assert result.statistics_density >= 1.0


class TestCitationDensity:
    """Tests for source attribution pattern detection."""

    def test_according_to(self) -> None:
        result = analyze_geo(
            "According to recent findings, the method works well. Many agree."
        )
        assert result.citation_density > 0

    def test_research_shows(self) -> None:
        result = analyze_geo(
            "Research shows that exercise improves mood. This is well known."
        )
        assert result.citation_density > 0

    def test_study_found(self) -> None:
        result = analyze_geo(
            "A study found that sleep affects performance. Rest is important."
        )
        assert result.citation_density > 0

    def test_parenthetical_year(self) -> None:
        result = analyze_geo(
            "The GEO framework (2024) proposes nine strategies. They work well."
        )
        assert result.citation_density > 0

    def test_et_al(self) -> None:
        result = analyze_geo(
            "Aggarwal et al. demonstrated the impact clearly. Results were strong."
        )
        assert result.citation_density > 0

    def test_published_in(self) -> None:
        result = analyze_geo(
            "The paper was published in Nature last month. It got attention."
        )
        assert result.citation_density > 0

    def test_no_citations(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.citation_density == pytest.approx(0.0)


class TestDefinitionDensity:
    """Tests for definitional pattern detection."""

    def test_defined_as(self) -> None:
        result = analyze_geo(
            "LIX is defined as a readability formula for text. It is widely used."
        )
        assert result.definition_density > 0

    def test_refers_to(self) -> None:
        result = analyze_geo(
            "GEO refers to optimizing content for generative engines. It matters."
        )
        assert result.definition_density > 0

    def test_is_a_type_of(self) -> None:
        result = analyze_geo(
            "A lemma is a type of lexical unit in linguistics. Words have lemmas."
        )
        assert result.definition_density > 0

    def test_known_as(self) -> None:
        result = analyze_geo(
            "The technique is known as prompt engineering. It takes practice."
        )
        assert result.definition_density > 0

    def test_no_definitions(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.definition_density == pytest.approx(0.0)


class TestQuotationDensity:
    """Tests for quoted passage detection."""

    def test_double_quotes(self) -> None:
        result = analyze_geo(
            'The expert said "this approach is fundamentally different" to reporters. '
            "Many were surprised."
        )
        assert result.quotation_density > 0

    def test_short_quotes_ignored(self) -> None:
        """Quotes shorter than 10 chars are not counted as substantive."""
        result = analyze_geo('He said "yes" to the proposal. Everyone cheered loudly.')
        assert result.quotation_density == pytest.approx(0.0)

    def test_no_quotations(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.quotation_density == pytest.approx(0.0)


class TestAuthorityScore:
    """Tests for authoritative tone vocabulary scoring."""

    def test_authority_words_detected(self) -> None:
        result = analyze_geo(
            "Research evidence demonstrates significant findings in the analysis. "
            "The methodology was validated and verified."
        )
        assert result.authority_score > 0

    def test_no_authority_words(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.authority_score == pytest.approx(0.0)

    def test_authority_score_bounded(self) -> None:
        """Authority score should be between 0 and 1."""
        result = analyze_geo(
            "Research evidence demonstrates significant findings in the analysis. "
            "The methodology was validated and verified."
        )
        assert 0.0 <= result.authority_score <= 1.0


class TestQuestionRatio:
    """Tests for question sentence detection."""

    def test_question_detected(self) -> None:
        result = analyze_geo(
            "What is GEO? It is a framework for optimizing content for AI systems."
        )
        assert result.question_ratio > 0

    def test_all_questions(self) -> None:
        result = analyze_geo(
            "What is the LIX score? How do you compute it? Why does it matter?"
        )
        assert result.question_ratio == pytest.approx(1.0)

    def test_no_questions(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.question_ratio == pytest.approx(0.0)

    def test_mixed_questions_and_statements(self) -> None:
        result = analyze_geo(
            "What is readability? Readability measures how easy text is to read. "
            "Why does it matter? Clear text reaches more people."
        )
        assert result.question_ratio == pytest.approx(0.5)


class TestListDensity:
    """Tests for list/bullet pattern detection."""

    def test_dash_list(self) -> None:
        text = (
            "The key benefits are as follows.\n"
            "- Improved clarity for readers.\n"
            "- Better structure and flow.\n"
            "- Higher engagement rates overall."
        )
        result = analyze_geo(text)
        assert result.list_density > 0

    def test_numbered_list(self) -> None:
        text = (
            "Follow these steps carefully.\n"
            "1. Open the file in your editor.\n"
            "2. Make the required changes.\n"
            "3. Save and close the file."
        )
        result = analyze_geo(text)
        assert result.list_density > 0

    def test_asterisk_list(self) -> None:
        text = (
            "Consider these options today.\n"
            "* Option A is the best choice.\n"
            "* Option B is a good backup.\n"
            "* Option C is the last resort."
        )
        result = analyze_geo(text)
        assert result.list_density > 0

    def test_no_lists(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.list_density == pytest.approx(0.0)


class TestFreshnessScore:
    """Tests for temporal reference detection."""

    def test_year_reference(self) -> None:
        result = analyze_geo(
            "In 2024 the framework was released to the public. It changed things."
        )
        assert result.freshness_score > 0

    def test_updated_on(self) -> None:
        result = analyze_geo(
            "This guide was updated on March 5 this year. Please read carefully."
        )
        assert result.freshness_score > 0

    def test_month_and_day(self) -> None:
        result = analyze_geo(
            "The event takes place on January 15 every year. Registration is open."
        )
        assert result.freshness_score > 0

    def test_as_of(self) -> None:
        result = analyze_geo(
            "As of 2024 the policy has been fully implemented. All teams comply."
        )
        assert result.freshness_score > 0

    def test_no_freshness_markers(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.freshness_score == pytest.approx(0.0)


class TestWordAndSentenceCounts:
    """Tests for basic count fields."""

    def test_word_count(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.word_count == 11

    def test_sentence_count(self) -> None:
        result = analyze_geo("The cat sat on the mat. It was warm and soft.")
        assert result.sentence_count == 2


class TestLanguageSupport:
    """Tests for non-English language support."""

    def test_norwegian_text(self) -> None:
        result = analyze_geo(
            "Ifølge en studie fra 2024 viser forskning at 73% av brukerne foretrekker "
            "denne metoden. Resultatene er signifikante.",
            language="nb",
        )
        assert isinstance(result, GEOResult)
        assert result.statistics_density > 0  # 73%
        assert result.freshness_score > 0  # 2024

    def test_swedish_text(self) -> None:
        result = analyze_geo(
            "Forskare har visat att metoden fungerar bra. "
            "Studien publicerades i en viktig tidskrift.",
            language="sv",
        )
        assert isinstance(result, GEOResult)
        assert result.sentence_count == 2


class TestIntegration:
    """Integration tests with rich text combining multiple GEO signals."""

    def test_high_geo_text(self) -> None:
        """Text designed with multiple GEO signals should score across signals."""
        text = (
            "According to a 2024 study by Aggarwal et al., 73% of content "
            "optimized for generative engines saw improved visibility. "
            'The lead researcher stated "these findings represent a '
            'fundamental shift in content strategy" at the conference. '
            "GEO is defined as the practice of optimizing content for "
            "AI-powered search systems."
        )
        result = analyze_geo(text)
        assert result.statistics_density > 0  # 73%
        assert result.citation_density > 0  # according to, et al.
        assert result.definition_density > 0  # is defined as
        assert result.quotation_density > 0  # quoted passage
        assert result.authority_score > 0  # fundamental, findings, research
        assert result.freshness_score > 0  # 2024

    def test_low_geo_text(self) -> None:
        """Plain conversational text should score low on GEO signals."""
        text = "The cat sat on the mat. It was warm and soft."
        result = analyze_geo(text)
        assert result.statistics_density == pytest.approx(0.0)
        assert result.citation_density == pytest.approx(0.0)
        assert result.definition_density == pytest.approx(0.0)
        assert result.quotation_density == pytest.approx(0.0)
        assert result.authority_score == pytest.approx(0.0)
        assert result.question_ratio == pytest.approx(0.0)
        assert result.list_density == pytest.approx(0.0)
        assert result.freshness_score == pytest.approx(0.0)

    def test_qa_structured_text(self) -> None:
        """Q&A structured content should have non-zero question ratio."""
        text = (
            "What is readability? "
            "Readability is defined as how easy text is to understand. "
            "Why does it matter? "
            "Research shows that clear text reaches more people."
        )
        result = analyze_geo(text)
        assert result.question_ratio == pytest.approx(0.5)
        assert result.definition_density > 0
        assert result.citation_density > 0
