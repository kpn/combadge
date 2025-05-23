from typing import Annotated

import pytest
from httpx import AsyncClient, Client
from pydantic import BaseModel, Field, ValidationError, validate_call
from typing_extensions import Protocol

from combadge.core.markers.method import wrap_with
from combadge.support.http.markers import QueryParam, http_method, path
from combadge.support.httpx.backends.async_ import HttpxBackend as AsyncHttpxBackend
from combadge.support.httpx.backends.sync import HttpxBackend as SyncHttpxBackend


class CurrentCondition(BaseModel):
    humidity: int
    temperature: Annotated[float, Field(alias="temp_C")]


class Weather(BaseModel):
    current: Annotated[list[CurrentCondition], Field(alias="current_condition")]


@pytest.mark.vcr
def test_weather_sync() -> None:
    class SupportsWttrIn(Protocol):
        @http_method("GET")
        @path("/{in_}")
        @wrap_with(validate_call)
        def get_weather(
            self,
            *,
            in_: Annotated[str, Field(min_length=1)],
            format_: Annotated[str, Field(min_length=1), QueryParam("format")] = "j1",
        ) -> Weather:
            raise NotImplementedError

    with SyncHttpxBackend(Client(base_url="https://wttr.in")) as backend:
        service = backend[SupportsWttrIn]

        response = service.get_weather(in_="amsterdam")
        assert response.current[0].humidity == 93
        assert response.current[0].temperature == 2

        with pytest.raises(ValidationError):
            service.get_weather(in_="")


@pytest.mark.vcr
async def test_weather_async() -> None:
    class SupportsWttrIn(Protocol):
        @http_method("GET")
        @path("/{in_}")
        @wrap_with(validate_call)
        async def get_weather(
            self,
            *,
            in_: Annotated[str, Field(min_length=1)],
            format_: Annotated[str, Field(min_length=1), QueryParam("format")] = "j1",
        ) -> Weather:
            raise NotImplementedError

    async with AsyncHttpxBackend(AsyncClient(base_url="https://wttr.in")) as backend:
        service = backend[SupportsWttrIn]
        with pytest.raises(ValidationError):
            await service.get_weather(in_="")
        response = await service.get_weather(in_="amsterdam")

    assert response.current[0].humidity == 71
    assert response.current[0].temperature == 8.0
