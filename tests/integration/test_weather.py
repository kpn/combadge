from typing import List

from httpx import AsyncClient, Client
from pydantic import BaseModel, Field, ValidationError
from pytest import mark, raises
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.http.markers import QueryParam, http_method, path
from combadge.support.httpx.backends.async_ import HttpxBackend as AsyncHttpxBackend
from combadge.support.httpx.backends.sync import HttpxBackend as SyncHttpxBackend


class CurrentCondition(BaseModel):
    humidity: int
    temperature: Annotated[float, Field(alias="temp_C")]


class Weather(BaseModel):
    current: Annotated[List[CurrentCondition], Field(alias="current_condition")]


@mark.vcr
def test_weather_sync() -> None:
    class SupportsWttrIn(Protocol):
        @http_method("GET")
        @path("/{in_}")
        def get_weather(
            self,
            *,
            in_: Annotated[str, Field(min_length=1)],
            format_: Annotated[str, Field(min_length=1), QueryParam("format")] = "j1",
        ) -> Weather:
            raise NotImplementedError

    backend = SyncHttpxBackend(Client(base_url="https://wttr.in"))
    service = bind(SupportsWttrIn, backend)  # type: ignore[type-abstract]
    response = service.get_weather(in_="amsterdam")

    assert response.current[0].humidity == 93
    assert response.current[0].temperature == 2

    with raises(ValidationError):
        service.get_weather(in_="")


@mark.vcr
async def test_weather_async() -> None:
    class SupportsWttrIn(Protocol):
        @http_method("GET")
        @path("/{in_}")
        async def get_weather(
            self,
            *,
            in_: Annotated[str, Field(min_length=1)],
            format_: Annotated[str, Field(min_length=1), QueryParam("format")] = "j1",
        ) -> Weather:
            raise NotImplementedError

    backend = AsyncHttpxBackend(AsyncClient(base_url="https://wttr.in"))
    service = bind(SupportsWttrIn, backend)  # type: ignore[type-abstract]
    response = await service.get_weather(in_="amsterdam")

    assert response.current[0].humidity == 71
    assert response.current[0].temperature == 8.0

    with raises(ValidationError):
        await service.get_weather(in_="")
