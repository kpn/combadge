import re
from pathlib import Path

from pytest import mark, param

CODE_BLOCK_RE = re.compile(r"^```python\n+# test_id=(\w+)\n+$(.*?)^```$", re.MULTILINE | re.DOTALL)
README = (Path(__file__).parent.parent.parent / "README.md").read_text()


@mark.parametrize(
    "code_block",
    [param(code_block, id=test_id) for (test_id, code_block) in CODE_BLOCK_RE.findall(README)],
)
@mark.vcr(decode_compressed_response=True)
def test_code_block(code_block: str) -> None:
    exec(code_block, {})
