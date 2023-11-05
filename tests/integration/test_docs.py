"""Tests code snippets in the `README.md` and `docs`."""

import re
from itertools import chain
from pathlib import Path
from textwrap import dedent
from typing import Iterator, NamedTuple

import pytest

CODE_BLOCK_RE = re.compile(r"""```python title="([^"]+)"[^\n]*(.+?)```""", re.MULTILINE | re.DOTALL)


def _discover_files() -> Iterator[Path]:
    yield Path("README.md")
    yield from Path("docs").rglob("*.md")


def _generate_params(path: Path) -> Iterator[NamedTuple]:
    for test_id, snippet in CODE_BLOCK_RE.findall(path.read_text()):
        yield pytest.param(snippet, id=f"{'-'.join(path.parts)}#{test_id}")


@pytest.mark.parametrize(
    "snippet",
    chain.from_iterable(_generate_params(path) for path in _discover_files()),
)
@pytest.mark.vcr(decode_compressed_response=True)
def test_documentation_snippet(snippet: str) -> None:
    exec(dedent(snippet), {})
