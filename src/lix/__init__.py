"""LIX — Readability and GEO scores for Scandinavian languages and English.

Computes LIX (Björnsson, 1968) and RIX (Anderson, 1983) readability
indices, plus GEO (Generative Engine Optimization) signals for AI visibility.
Supports Norwegian (Bokmål/Nynorsk), Swedish, Danish, and English text.

Example:
    >>> import lix
    >>> result = lix.compute("The cat sat on the mat. It was warm.", language="en")
    >>> result.lix
    10.0
    >>> result.difficulty
    <Difficulty.VERY_EASY: 'very_easy'>
"""

from __future__ import annotations

from lix.core import compute, compute_lix, compute_rix
from lix.geo import GEOResult, analyze_geo
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
    "GEOResult",
    "Language",
    "ReadabilityResult",
    "analyze_geo",
    "classify_lix",
    "compute",
    "compute_lix",
    "compute_rix",
]
