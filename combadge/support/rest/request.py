from typing import Any, Dict, Optional

from pydantic import BaseModel

from combadge.support.http.abc import RequiresMethod, RequiresPath, SupportsQueryParams
from combadge.support.rest.abc import SupportsJson


class Request(RequiresMethod, RequiresPath, SupportsJson, SupportsQueryParams, BaseModel):
    """Backend-agnostic REST request."""

    def json_dict(self) -> Optional[Dict[str, Any]]:
        """Convert the JSON body to a dictionary."""
        return json.dict(by_alias=True) if (json := self.json_) is not None else None
