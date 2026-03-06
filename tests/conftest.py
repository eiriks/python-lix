"""Shared test fixtures for LIX test suite."""

from __future__ import annotations

import pytest


@pytest.fixture()
def simple_norwegian_text() -> str:
    """A simple Norwegian text with known readability properties."""
    return "Katten satt på matta. Den var svart og liten."


@pytest.fixture()
def complex_norwegian_text() -> str:
    """A more complex Norwegian text with longer words."""
    return (
        "Stortingsrepresentanten diskuterte grunnlovsforslaget "
        "i interpellasjonsdebattene. Statsministeren argumenterte "
        "overbevisende for budsjettproposisjonen."
    )


@pytest.fixture()
def danish_text() -> str:
    """A Danish text for cross-language testing."""
    return "Katten sad på måtten. Den var sort og lille."


@pytest.fixture()
def swedish_text() -> str:
    """A Swedish text for cross-language testing."""
    return "Katten satt på mattan. Den var svart och liten."


@pytest.fixture()
def simple_english_text() -> str:
    """A simple English text with known readability properties."""
    return "The cat sat on the mat. It was warm and soft."


@pytest.fixture()
def complex_english_text() -> str:
    """A more complex English text with longer words."""
    return (
        "The parliamentary representative discussed the constitutional "
        "amendment during the interpellation debates. The prime minister "
        "argued convincingly for the appropriations budget."
    )
