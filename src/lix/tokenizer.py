"""Tokenization utilities for text analysis."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from lix.types import LONG_WORD_THRESHOLD, Language

if TYPE_CHECKING:
    from collections.abc import Sequence

# ── Abbreviations that should NOT trigger sentence boundaries ──────────────
# Periods in these tokens are not sentence-enders.
_ABBREVIATIONS: dict[Language, frozenset[str]] = {
    "nb": frozenset(
        {
            "bl.a",
            "f.eks",
            "kl",
            "ca",
            "dvs",
            "mfl",
            "osv",
            "evt",
            "pga",
            "ifm",
            "mht",
            "o.l",
            "etc",
            "nr",
            "tlf",
            "jf",
            "St.meld",
            "Prop",
            "mrd",
            "mill",
            "dept",
        }
    ),
    "nn": frozenset(
        {
            "bl.a",
            "t.d",
            "kl",
            "ca",
            "dvs",
            "mfl",
            "osv",
            "evt",
            "pga",
            "ifm",
            "mht",
            "o.l",
            "etc",
            "nr",
            "tlf",
            "jf",
        }
    ),
    "da": frozenset(
        {
            "bl.a",
            "f.eks",
            "kl",
            "ca",
            "dvs",
            "mfl",
            "osv",
            "evt",
            "pga",
            "ifm",
            "mht",
            "o.l",
            "etc",
            "nr",
            "tlf",
            "jf",
        }
    ),
    "sv": frozenset(
        {
            "bl.a",
            "t.ex",
            "kl",
            "ca",
            "dvs",
            "mfl",
            "osv",
            "evt",
            "pga",
            "ifm",
            "mht",
            "o.d",
            "etc",
            "nr",
            "tlf",
            "jfr",
            "fr.o.m",
            "t.o.m",
        }
    ),
    "en": frozenset(
        {
            # Titles
            "Mr",
            "Mrs",
            "Ms",
            "Dr",
            "Prof",
            "Rev",
            "Gen",
            "Gov",
            "Sgt",
            "Jr",
            "Sr",
            "St",
            # Academic / professional
            "Vol",
            "No",
            "Fig",
            "Ed",
            "Dept",
            "Corp",
            "Inc",
            "Ltd",
            "Co",
            # Latin abbreviations
            "e.g",
            "i.e",
            "vs",
            "etc",
            "approx",
            "est",
            # Country / organisation abbreviations
            "U.S",
            "U.K",
            "U.N",
        }
    ),
}

# Common abbreviations shared across all Scandinavian languages
_SHARED_ABBREVIATIONS: frozenset[str] = frozenset(
    {
        "bl.a",
        "ca",
        "dvs",
        "etc",
        "evt",
        "kl",
        "mfl",
        "nr",
        "osv",
        "pga",
    }
)

# ── Sentence boundary pattern ─────────────────────────────────────────────
# Matches sentence-ending punctuation followed by whitespace and an uppercase
# letter (including Scandinavian characters Æ Ø Å Ä Ö).
_SENTENCE_BOUNDARY: re.Pattern[str] = re.compile(
    r"([.!?]+)\s+(?=[A-ZÆØÅÄÖ])",
)

# ── Word extraction ───────────────────────────────────────────────────────
# Matches sequences of word characters including hyphens for compound words
# and Scandinavian characters.
_WORD_PATTERN: re.Pattern[str] = re.compile(
    r"[a-zæøåäöA-ZÆØÅÄÖ\-]+",
)


def _get_abbreviations(language: Language) -> frozenset[str]:
    """Return the abbreviation set for a given language.

    Falls back to the shared set if the language is not specifically mapped.

    Args:
        language: ISO 639-1 language code.

    Returns:
        Frozen set of abbreviation strings (without trailing period).
    """
    return _ABBREVIATIONS.get(language, _SHARED_ABBREVIATIONS)


def split_sentences(text: str, language: Language = "nb") -> list[str]:
    """Split text into sentences, handling Scandinavian abbreviations.

    Uses punctuation-based boundary detection while avoiding false splits
    on common abbreviations (e.g. 'bl.a.', 'f.eks.', 't.ex.').

    Args:
        text: The input text to split.
        language: Language code for abbreviation handling.

    Returns:
        A list of sentence strings. Empty input returns an empty list.
    """
    if not text or not text.strip():
        return []

    abbreviations = _get_abbreviations(language)

    # Replace abbreviation periods with placeholders to avoid false splits
    protected = text
    for abbr in sorted(abbreviations, key=len, reverse=True):
        # Match the abbreviation with its trailing period
        pattern = re.compile(re.escape(abbr) + r"\.", re.IGNORECASE)
        protected = pattern.sub(abbr.replace(".", "\x00") + "\x00", protected)

    # Split on sentence boundaries
    parts = _SENTENCE_BOUNDARY.split(protected)

    # Reassemble: parts alternate between text and delimiter
    sentences: list[str] = []
    i = 0
    while i < len(parts):
        segment = parts[i]
        # Attach the punctuation back to the sentence
        if i + 1 < len(parts) and re.fullmatch(r"[.!?]+", parts[i + 1]):
            segment += parts[i + 1]
            i += 2
        else:
            i += 1
        # Restore placeholders back to periods
        segment = segment.replace("\x00", ".")
        segment = segment.strip()
        if segment:
            sentences.append(segment)

    return sentences


def extract_words(text: str) -> list[str]:
    """Extract words from text, stripping punctuation.

    Handles hyphenated compounds (e.g. 'x-ray') as single words.
    Strips leading/trailing hyphens.

    Args:
        text: The input text.

    Returns:
        A list of word strings. Empty input returns an empty list.
    """
    if not text:
        return []
    words = _WORD_PATTERN.findall(text)
    # Strip leading/trailing hyphens from each match
    return [w.strip("-") for w in words if w.strip("-")]


def count_long_words(words: Sequence[str]) -> int:
    """Count words with more than LONG_WORD_THRESHOLD characters.

    Per Björnsson (1968), a 'long word' has more than 6 characters (i.e. ≥7).

    Args:
        words: Sequence of word strings.

    Returns:
        The number of long words.
    """
    return sum(1 for w in words if len(w) > LONG_WORD_THRESHOLD)
