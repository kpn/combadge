from typing import List

from httpx import Client
from pydantic import BaseModel, Field
from pytest import mark
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.rest.marks import QueryParam, method, path


@mark.vcr
def test_weather() -> None:
    class CurrentCondition(BaseModel):
        humidity: int
        temperature: Annotated[float, Field(alias="temp_C")]

    class Weather(BaseModel):
        current: Annotated[List[CurrentCondition], Field(alias="current_condition")]

    class SupportsWttrIn(Protocol):
        @method("GET")
        @path("/{in_}")
        def get_weather(
            self,
            *,
            in_: str,
            format_: Annotated[str, QueryParam("format")],
        ) -> Weather:
            raise NotImplementedError

    backend = HttpxBackend(Client(base_url="https://wttr.in"))
    service = bind(SupportsWttrIn, backend)  # type: ignore[type-abstract]
    response = service.get_weather(in_="amsterdam", format_="j1")

    assert response.current[0].humidity == 93
    assert response.current[0].temperature == 2