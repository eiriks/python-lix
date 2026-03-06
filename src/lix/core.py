"""Core readability score computation.

Implements the LIX (Björnsson, 1968) and RIX (Anderson, 1983) formulas
for Scandinavian languages and English.
"""

from __future__ import annotations

from lix.tokenizer import count_long_words, extract_words, split_sentences
from lix.types import (
    Language,
    ReadabilityResult,
    classify_lix,
)


def compute_lix(text: str, language: Language = "nb") -> float:
    """Compute the LIX readability score for the given text.

    LIX = (words / sentences) + (long_words * 100 / words)

    Developed by Carl-Hugo Björnsson (1968). Long words are those with
    more than 6 characters (i.e. ≥7).

    Args:
        text: The input text to analyze. Must be non-empty.
        language: ISO 639-1 code for tokenization ('nb', 'nn', 'da', 'sv', 'en').

    Returns:
        The LIX score as a float. Lower scores indicate easier text.

    Raises:
        ValueError: If text is empty or contains no detectable sentences.
    """
    words, sentence_count, long_word_count = _analyze(text, language)
    word_count = len(words)

    return word_count / sentence_count + (long_word_count * 100) / word_count


def compute_rix(text: str, language: Language = "nb") -> float:
    """Compute the RIX readability score for the given text.

    RIX = long_words / sentences

    Developed by Jonathan Anderson (1983) as a simplified alternative to LIX.
    Long words are those with more than 6 characters (i.e. ≥7), consistent
    with the LIX definition.

    Args:
        text: The input text to analyze. Must be non-empty.
        language: ISO 639-1 code for tokenization ('nb', 'nn', 'da', 'sv', 'en').

    Returns:
        The RIX score as a float. Higher scores indicate harder text.

    Raises:
        ValueError: If text is empty or contains no detectable sentences.
    """
    _words, sentence_count, long_word_count = _analyze(text, language)

    return long_word_count / sentence_count


def compute(text: str, language: Language = "nb") -> ReadabilityResult:
    """Compute both LIX and RIX scores and return a full result.

    This is the main entry point for the library. It computes all metrics
    in a single pass over the text.

    Args:
        text: The input text to analyze. Must be non-empty.
        language: ISO 639-1 code for tokenization ('nb', 'nn', 'da', 'sv', 'en').

    Returns:
        A ReadabilityResult with LIX, RIX, difficulty category, and counts.

    Raises:
        ValueError: If text is empty or contains no detectable sentences.

    Example:
        >>> import lix
        >>> result = lix.compute("Katten satt på matta. Den var varm.", language="nb")
        >>> result.difficulty
        <Difficulty.VERY_EASY: 'very_easy'>
    """
    words, sentence_count, long_word_count = _analyze(text, language)
    word_count = len(words)

    lix_score = word_count / sentence_count + (long_word_count * 100) / word_count
    rix_score = long_word_count / sentence_count

    return ReadabilityResult(
        lix=lix_score,
        rix=rix_score,
        difficulty=classify_lix(lix_score),
        word_count=word_count,
        sentence_count=sentence_count,
        long_word_count=long_word_count,
        language=language,
    )


def _analyze(
    text: str,
    language: Language,
) -> tuple[list[str], int, int]:
    """Validate input and extract core metrics.

    Args:
        text: The input text.
        language: Language code for tokenization.

    Returns:
        A tuple of (words, sentence_count, long_word_count).

    Raises:
        ValueError: If text is empty, has no words, or has no sentences.
    """
    if not text or not text.strip():
        raise ValueError("Text must be non-empty.")

    sentences = split_sentences(text, language)
    if not sentences:
        raise ValueError(
            "No sentences detected. Text must contain at least one sentence "
            "ending with '.', '!', or '?'."
        )

    words = extract_words(text)
    if not words:
        raise ValueError("No words detected in the text.")

    sentence_count = len(sentences)
    long_word_count = count_long_words(words)

    return words, sentence_count, long_word_count
