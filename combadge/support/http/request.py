from typing import Any, Dict, List

from pydantic import BaseModel

from combadge.support.http.abc import RequiresMethod, RequiresPath, SupportsFormData, SupportsJson, SupportsQueryParams


class Request(RequiresMethod, RequiresPath, SupportsJson, SupportsQueryParams, SupportsFormData, BaseModel):
    """Backend-agnostic REST request."""

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert the JSON body and loose JSON fields into a dictionary."""
        dict_ = self.json_fields.copy()
        if (json := self.json_) is not None:
            dict_.update(json.dict(by_alias=True))
        return dict_

    def to_form_data(self) -> Dict[str, List[Any]]:
        """Convert the form data and loose form fields into a dictionary."""
        form_fields = self.form_fields.copy()
        if (form_data := self.form_data) is not None:
            for name, value in form_data.dict(by_alias=True).items():
                self.append_form_field(name, value)
        return form_fields
