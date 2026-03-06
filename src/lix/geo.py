"""Generative Engine Optimization (GEO) text analysis.

Computes text-level signals that correlate with visibility in generative
AI systems (ChatGPT, Perplexity, Google AI Overviews, Claude).

Based on research from Aggarwal et al. (2024) "GEO: Generative Engine
Optimization" (ACM SIGKDD) which measured the impact of content strategies
on AI citation rates.

Example:
    >>> import lix
    >>> result = lix.analyze_geo(
    ...     "According to a 2024 study, 73% prefer AI."
    ... )
    >>> result.statistics_density
    1.0
    >>> result.citation_density
    1.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from lix.tokenizer import extract_words, split_sentences

# ── Regex patterns for GEO signal detection ──────────────────────────────

# Statistics: percentages, dollar amounts, large numbers, comparisons
_STAT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\d+(\.\d+)?%"),  # 73%, 4.5%
    re.compile(r"\$[\d,]+(\.\d+)?"),  # $1,000, $4.5
    re.compile(r"€[\d,]+(\.\d+)?"),  # €1,000
    re.compile(r"\d+(\.\d+)?\s*x\s+(faster|better|more|worse|larger|smaller)", re.I),
    re.compile(r"\d[\d,]*\s+(million|billion|trillion)", re.I),
    re.compile(r"\d+(\.\d+)?\s+(times|percent|percentage)", re.I),
]

# Citation / source attribution patterns
_CITATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"according\s+to", re.I),
    re.compile(r"research\s+(shows?|found|indicates?|suggests?|demonstrates?)", re.I),
    re.compile(r"stud(y|ies)\s+(shows?|found|indicates?|suggests?|reveals?)", re.I),
    re.compile(r"(data|evidence)\s+(shows?|suggests?|indicates?)", re.I),
    re.compile(r"(published|reported)\s+(in|by)", re.I),
    re.compile(r"(researchers?|scientists?|experts?)\s+(at|from|have)", re.I),
    re.compile(r"\(\d{4}\)"),  # (2024) style citations
    re.compile(r"et\s+al\.?", re.I),  # et al.
]

# Direct definition patterns
_DEFINITION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"is\s+defined\s+as", re.I),
    re.compile(r"refers?\s+to", re.I),
    re.compile(r"(is|are)\s+a\s+(type|form|kind)\s+of", re.I),
    re.compile(r"(means?|meaning)\s+that", re.I),
    re.compile(r"can\s+be\s+described\s+as", re.I),
    re.compile(r"(is|are)\s+known\s+as", re.I),
    re.compile(r"(is|are)\s+(the\s+)?(process|practice|act)\s+of", re.I),
]

# Quotation detection (text within quotation marks)
_QUOTATION_PATTERN: re.Pattern[str] = re.compile(
    r'["\u201c\u201d\u00ab\u00bb]'  # ", ", ", «, »
    r"[^\"'\u201c\u201d\u00ab\u00bb]{10,}"  # at least 10 chars inside
    r'["\u201c\u201d\u00ab\u00bb]',
)

# Question patterns (sentences ending with ?)
_QUESTION_PATTERN: re.Pattern[str] = re.compile(r"\?\s*$")

# List/bullet patterns (lines starting with list markers)
_LIST_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*(?:[-*•]|\d+[.)]\s)",
    re.MULTILINE,
)

# Authoritative tone vocabulary
_AUTHORITY_WORDS: frozenset[str] = frozenset(
    {
        "analysis",
        "assessed",
        "comprehensive",
        "conclusion",
        "confirmed",
        "critical",
        "demonstrated",
        "determined",
        "essential",
        "established",
        "evaluated",
        "evidence",
        "examination",
        "expert",
        "findings",
        "fundamental",
        "identified",
        "investigation",
        "methodology",
        "observed",
        "principle",
        "recommended",
        "research",
        "revealed",
        "significant",
        "systematic",
        "validated",
        "verified",
    }
)

# Freshness markers (dates, year references, "updated")
_FRESHNESS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b20[12]\d\b"),  # 2010-2029
    re.compile(r"\b(updated|revised|published)\s+(on|in)\b", re.I),
    re.compile(
        r"\b(January|February|March|April|May|June|July|August"
        r"|September|October|November|December)\s+\d{1,2}",
        re.I,
    ),
    re.compile(r"\bas\s+of\s+\d", re.I),  # "as of 2024"
]

# Minimum word count for meaningful analysis
_MIN_WORDS_FOR_ANALYSIS: int = 3


@dataclass(frozen=True, slots=True)
class GEOResult:
    """Result of GEO (Generative Engine Optimization) text analysis.

    All density metrics are expressed as counts per sentence, making them
    comparable across texts of different lengths.

    Attributes:
        statistics_density: Statistical references per sentence.
            Higher values indicate more data-driven content.
            Impact: +37% AI visibility (Aggarwal et al., 2024).
        citation_density: Source attribution patterns per sentence.
            Higher values indicate more verifiable claims.
            Impact: +30% AI visibility.
        definition_density: Definitional patterns per sentence.
            Higher values indicate more explanatory content.
            Impact: +28% AI visibility.
        quotation_density: Quoted passages per sentence.
            Higher values indicate more attributed speech/text.
            Impact: +28% AI visibility.
        authority_score: Fraction of words that signal authoritative tone
            (0.0 to 1.0). Higher = more authoritative vocabulary.
            Impact: +24.5% AI visibility.
        question_ratio: Fraction of sentences that are questions (0.0 to 1.0).
            Non-zero values suggest Q&A structure, which improves
            extractability by AI systems.
        list_density: List/bullet items per sentence.
            Structured content is more easily extracted by AI.
        freshness_score: Temporal reference density per sentence.
            Content with dates and recency markers scores higher for
            time-sensitive queries.
        word_count: Total words in the analyzed text.
        sentence_count: Total sentences in the analyzed text.
    """

    statistics_density: float
    citation_density: float
    definition_density: float
    quotation_density: float
    authority_score: float
    question_ratio: float
    list_density: float
    freshness_score: float
    word_count: int
    sentence_count: int


def analyze_geo(text: str, language: str = "en") -> GEOResult:
    """Analyze text for Generative Engine Optimization signals.

    Computes density metrics that correlate with content visibility in
    generative AI systems. Based on the GEO framework by Aggarwal et al.
    (2024, ACM SIGKDD).

    All density metrics are normalized per sentence to allow comparison
    across texts of different lengths.

    Args:
        text: The input text to analyze. Must be non-empty and contain
            at least one sentence.
        language: Language code for sentence tokenization. Defaults to
            "en". Supports the same codes as ``lix.compute``.

    Returns:
        A GEOResult with all GEO signal metrics.

    Raises:
        ValueError: If text is empty or contains no detectable sentences.

    Example:
        >>> result = analyze_geo(
        ...     "According to a 2024 study, 73% of users prefer AI search. "
        ...     "This represents a significant shift in behavior."
        ... )
        >>> result.statistics_density  # 1 stat / 2 sentences
        0.5
        >>> result.citation_density  # 1 citation / 2 sentences
        0.5
    """
    if not text or not text.strip():
        raise ValueError("Text must be non-empty.")

    sentences = split_sentences(text, language)  # type: ignore[arg-type]
    if not sentences:
        raise ValueError(
            "No sentences detected. Text must contain at least one sentence "
            "ending with '.', '!', or '?'."
        )

    words = extract_words(text)
    if len(words) < _MIN_WORDS_FOR_ANALYSIS:
        raise ValueError(
            f"Text must contain at least {_MIN_WORDS_FOR_ANALYSIS} words "
            f"for meaningful analysis, got {len(words)}."
        )

    sentence_count = len(sentences)
    word_count = len(words)

    # Count pattern matches across the full text
    stat_count = _count_pattern_matches(text, _STAT_PATTERNS)
    citation_count = _count_pattern_matches(text, _CITATION_PATTERNS)
    definition_count = _count_pattern_matches(text, _DEFINITION_PATTERNS)
    quotation_count = len(_QUOTATION_PATTERN.findall(text))
    list_count = len(_LIST_PATTERN.findall(text))
    freshness_count = _count_pattern_matches(text, _FRESHNESS_PATTERNS)

    # Question ratio: fraction of sentences that are questions
    question_count = sum(1 for s in sentences if _QUESTION_PATTERN.search(s))

    # Authority score: fraction of words that are authority vocabulary
    words_lower = [w.lower() for w in words]
    authority_word_count = sum(1 for w in words_lower if w in _AUTHORITY_WORDS)

    return GEOResult(
        statistics_density=stat_count / sentence_count,
        citation_density=citation_count / sentence_count,
        definition_density=definition_count / sentence_count,
        quotation_density=quotation_count / sentence_count,
        authority_score=authority_word_count / word_count,
        question_ratio=question_count / sentence_count,
        list_density=list_count / sentence_count,
        freshness_score=freshness_count / sentence_count,
        word_count=word_count,
        sentence_count=sentence_count,
    )


def _count_pattern_matches(
    text: str,
    patterns: list[re.Pattern[str]],
) -> int:
    """Count total non-overlapping matches across multiple regex patterns.

    Args:
        text: The text to search.
        patterns: List of compiled regex patterns.

    Returns:
        Total match count across all patterns.
    """
    return sum(len(p.findall(text)) for p in patterns)
