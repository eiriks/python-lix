"""Type definitions for readability score computation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

# Supported Scandinavian languages
Language = Literal["nb", "nn", "da", "sv"]
"""ISO 639-1 language codes: nb=Bokmål, nn=Nynorsk, da=Danish, sv=Swedish."""

LONG_WORD_THRESHOLD: int = 6
"""Words with more than this many characters are considered 'long words'."""


class Difficulty(Enum):
    """LIX score difficulty categories (Björnsson, 1968)."""

    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


def classify_lix(score: float) -> Difficulty:
    """Classify a LIX score into a difficulty category.

    Args:
        score: The LIX score to classify.

    Returns:
        The difficulty category for the given score.
    """
    if score < 25:
        return Difficulty.VERY_EASY
    if score < 35:
        return Difficulty.EASY
    if score < 45:
        return Difficulty.MEDIUM
    if score < 55:
        return Difficulty.HARD
    return Difficulty.VERY_HARD


@dataclass(frozen=True, slots=True)
class ReadabilityResult:
    """Result of a readability score computation.

    Attributes:
        lix: The LIX readability score. Lower = easier to read.
        rix: The RIX readability score (long words per sentence).
        difficulty: Human-readable difficulty category derived from LIX.
        word_count: Total number of words in the text.
        sentence_count: Total number of sentences detected.
        long_word_count: Number of words longer than 6 characters.
        language: The language code used for tokenization.
    """

    lix: float
    rix: float
    difficulty: Difficulty
    word_count: int
    sentence_count: int
    long_word_count: int
    language: Language
