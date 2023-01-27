# `combadge`

> 🖖 Application to the service, please respond!

[![Checks](https://img.shields.io/github/checks-status/kpn/combadge/main)](https://github.com/kpn/combadge/actions/workflows/check.yaml)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/kpn/combadge)

## Quickstart

### Declare a request model

```python
from typing import Annotated

from pydantic import BaseModel, Field


class NumberToWordsRequest(BaseModel):
    number: Annotated[int, Field(alias="ubiNum")]
```
