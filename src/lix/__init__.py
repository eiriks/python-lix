"""LIX — Readability scores for Scandinavian languages.

Computes LIX (Björnsson, 1968) and RIX (Anderson, 1983) readability
indices for Norwegian (Bokmål/Nynorsk), Swedish, and Danish text.

Example:
    >>> import lix
    >>> result = lix.compute("Katten satt på matta. Den var varm.")
    >>> result.lix
    10.0
    >>> result.difficulty
    <Difficulty.VERY_EASY: 'very_easy'>
"""

from __future__ import annotations

from lix.core import compute, compute_lix, compute_rix
from lix.types import (
    LONG_WORD_THRESHOLD,
    Difficulty,
    Language,
    ReadabilityResult,
    classify_lix,
)

__all__ = [
    "LONG_WORD_THRESHOLD",
    "Difficulty",
    "Language",
    "ReadabilityResult",
    "classify_lix",
    "compute",
    "compute_lix",
    "compute_rix",
]
