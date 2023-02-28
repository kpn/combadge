from typing import Any, Dict, Optional

from pydantic import BaseModel

from combadge.support.http.abc import RequiresMethod, RequiresPath, SupportsQueryParams
from combadge.support.rest.abc import SupportsJson


class Request(RequiresMethod, RequiresPath, SupportsJson, SupportsQueryParams, BaseModel):
    """Backend-agnostic REST request."""

    def json_dict(self) -> Optional[Dict[str, Any]]:
        """Convert the JSON body to a dictionary."""
        dict_ = self.json_fields
        if json := self.json_:
            dict_.update(json.dict(by_alias=True))
        return dict_
