# AGENTS.md — LIX Readability Library

Implements the LIX (Björnsson, 1968) and RIX (Anderson, 1983) formulas
for Scandinavian languages and English.
## Project Overview

LIX is a Python library for computing readability scores (LIX, RIX, and related metrics).
Open-source, minimal dependencies, typed, well-tested.

- **Language**: Python 3.12+
- **Package manager**: [uv](https://docs.astral.sh/uv/)
- **Linter/formatter**: [ruff](https://docs.astral.sh/ruff/)
- **Security**: [bandit](https://bandit.readthedocs.io/)
- **Testing**: [pytest](https://docs.pytest.org/)
- **Type checking**: [mypy](https://mypy.readthedocs.io/) (strict mode)

---

## Build & Run Commands

### Environment Setup

```bash
uv sync                     # Install all dependencies (incl. dev)
uv sync --no-dev            # Install production dependencies only
```

### Lint & Format

```bash
uv run ruff check .         # Lint (find issues)
uv run ruff check . --fix   # Lint and auto-fix
uv run ruff format .        # Format all files
uv run ruff format --check .  # Check formatting without changing files
```

### Type Checking

```bash
uv run mypy src/            # Type-check the source tree
```

### Security Scanning

```bash
uv run bandit -r src/       # Scan for security issues
```

### Testing

```bash
uv run pytest                           # Run all tests
uv run pytest tests/test_core.py         # Run a single test file
uv run pytest tests/test_core.py::TestComputeLix::test_known_score  # Run one test
uv run pytest -x                        # Stop on first failure
uv run pytest -k "lix and not slow"     # Run tests matching expression
uv run pytest --cov=lix --cov-report=term-missing  # With coverage
```

### Full CI Check (run before committing)

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run bandit -r src/ && uv run pytest
```

---

## Project Structure

```
LIX/
├── AGENTS.md
├── pyproject.toml          # Project metadata, dependencies, tool config
├── uv.lock                 # Locked dependencies
├── LICENSE
├── README.md
├── src/
│   └── lix/
│       ├── __init__.py     # Public API exports
│       ├── core.py         # LIX/RIX score computation
│       ├── tokenizer.py    # Sentence/word tokenization
│       ├── types.py        # TypedDicts, dataclasses, type aliases
│       └── py.typed        # PEP 561 marker
└── tests/
    ├── __init__.py
    ├── conftest.py         # Shared fixtures
    ├── test_core.py
    └── test_tokenizer.py
```

---

## Code Style

### Formatting (enforced by ruff)

- **Line length**: 88 characters max
- **Quotes**: Double quotes for strings
- **Trailing commas**: Always on multi-line structures
- **Indentation**: 4 spaces, no tabs

### Imports

Order enforced by ruff (`I` rules). Always use this grouping:

```python
# 1. Standard library
from collections.abc import Sequence
from dataclasses import dataclass

# 2. Third-party
import pytest

# 3. Local/project
from lix.core import compute_lix
from lix.types import ReadabilityResult
```

- Use `from __future__ import annotations` at the top of every module
- Prefer `from collections.abc import X` over `from typing import X` for runtime types
- Never use wildcard imports (`from x import *`)

### Naming Conventions

| Element          | Style            | Example                  |
|------------------|------------------|--------------------------|
| Modules          | snake_case       | `tokenizer.py`           |
| Classes          | PascalCase       | `ReadabilityResult`      |
| Functions        | snake_case       | `compute_lix`            |
| Constants        | UPPER_SNAKE_CASE | `LONG_WORD_THRESHOLD`    |
| Private members  | `_leading_under`  | `_split_sentences`       |
| Type aliases     | PascalCase       | `TokenList`              |

### Type Annotations

- **All public functions** must have full type annotations (params + return)
- **Private/internal** functions: annotations strongly recommended
- Use `str | None` union syntax (not `Optional[str]`)
- Use `X | Y` union syntax (not `Union[X, Y]`)
- Use built-in generics: `list[str]`, `dict[str, int]` (not `List`, `Dict`)
- Use `Self` from `typing` for fluent/builder patterns
- Prefer `Sequence` / `Mapping` in function parameters over concrete types

### Docstrings

Use Google-style docstrings on all public functions and classes:

```python
def compute_lix(text: str) -> float:
    """Compute the LIX readability score for the given text.

    The LIX formula: (words / sentences) + (long_words * 100 / words)
    where long words have more than 6 characters.

    Args:
        text: The input text to analyze. Must be non-empty.

    Returns:
        The LIX score as a float. Lower scores indicate easier text.

    Raises:
        ValueError: If text is empty or contains no sentences.
    """
```

### Error Handling

- Raise specific exceptions: `ValueError`, `TypeError` — never bare `Exception`
- Include actionable error messages: `raise ValueError(f"Expected non-empty text, got {len(text)} chars")`
- Never silently swallow exceptions (no empty `except` or `except: pass`)
- Use custom exceptions sparingly; only when callers need to distinguish error types
- Document raised exceptions in docstrings

### Constants & Magic Numbers

- No magic numbers in logic — define named constants
- Constants go in the module that uses them, or in `types.py` if shared

```python
LONG_WORD_THRESHOLD: int = 6  # Characters; words longer than this are "long words"
```

### Data Structures

- Use `@dataclass(frozen=True, slots=True)` for value objects
- Use `TypedDict` for dict shapes passed across boundaries
- Avoid mutable default arguments

```python
@dataclass(frozen=True, slots=True)
class ReadabilityResult:
    lix: float
    word_count: int
    sentence_count: int
    long_word_count: int
```

---

## Testing Conventions

- Test files mirror source: `src/lix/core.py` → `tests/test_core.py`
- Test function names: `test_<function>_<scenario>` (e.g., `test_compute_lix_empty_text_raises`)
- Use `pytest.raises` for expected exceptions
- Use `pytest.approx` for float comparisons
- Fixtures go in `conftest.py` when shared across files
- Parametrize over edge cases rather than writing repetitive tests

```python
@pytest.mark.parametrize("text,expected", [
    ("The cat sat.", pytest.approx(5.0, abs=0.1)),
    ("Short.", pytest.approx(0.0, abs=0.1)),
])
def test_compute_lix_known_scores(text: str, expected: float) -> None:
    assert compute_lix(text) == expected
```

---

## Git & Workflow

- Branch from `main`; merge via PR
- Commit messages: imperative mood, concise (`Add RIX score computation`, `Fix sentence boundary detection`)
- Do **not** commit without being explicitly asked
- Run the full CI check before committing

---

## Do NOT

- Suppress type errors (`type: ignore`, `Any` casts) without a comment explaining why
- Add runtime dependencies without discussing with the user first
- Modify the public API surface without discussing with the user first
- Write Python < 3.12 compatibility shims (we target 3.12+ only)
- Use `print()` for output in library code (raise or return instead)
