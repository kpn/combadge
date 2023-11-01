from http import HTTPStatus

from httpx import Response
from pydantic import BaseModel, RootModel

from combadge.support.http.aliases import Content, Reason, StatusCode
from combadge.support.httpx.backends.base import BaseHttpxBackend


def test_aliases() -> None:
    class Model(BaseModel):
        status_code: StatusCode[HTTPStatus]
        reason: Reason[str]
        content: Content[bytes]

    model = BaseHttpxBackend._parse_response(Response(200, text="hello world"), RootModel[Model])

    assert model.status_code == HTTPStatus.OK
    assert model.reason == "OK"
    assert model.content == b"hello world"
