from typing import Any, Dict, Optional

from pydantic import BaseModel

from combadge.support.http.abc import SupportsBody
from combadge.support.rest.abc import RequiresMethod, RequiresPath, SupportsQueryParams


class Request(RequiresMethod, RequiresPath, SupportsBody, SupportsQueryParams, BaseModel):
    """Backend-agnostic REST request."""

    def body_dict(self) -> Optional[Dict[str, Any]]:
        """Convert the body to a dictionary."""
        return body.dict(by_alias=True) if (body := self.body) is not None else None
