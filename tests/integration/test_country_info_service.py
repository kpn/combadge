from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Protocol

import pytest
from pydantic import BaseModel, Field
from zeep import Client

from combadge.core.errors import BackendError
from combadge.support.common import Body
from combadge.support.soap.markers import operation_name
from combadge.support.zeep.backends.sync import ZeepBackend


class Continent(BaseModel):
    code: Annotated[str, Field(alias="sCode")]
    name: Annotated[str, Field(alias="sName")]


class SupportsCountryInfo(Protocol):
    @operation_name("ListOfContinentsByName")
    @abstractmethod
    def list_of_continents_by_name(self) -> Body[list[Continent]]:
        raise NotImplementedError

    @operation_name("InvalidOperation")
    def invalid_operation(self) -> None:
        raise NotImplementedError


@pytest.fixture
def country_info_service() -> Iterable[SupportsCountryInfo]:
    with Client(wsdl=str(Path(__file__).parent / "wsdl" / "CountryInfoService.wsdl")) as client:
        yield ZeepBackend(client.service)[SupportsCountryInfo]  # type: ignore[type-abstract]


@pytest.mark.vcr(decode_compressed_response=True)
def test_happy_path(country_info_service: SupportsCountryInfo) -> None:
    continents = country_info_service.list_of_continents_by_name()

    assert isinstance(continents, list)
    assert len(continents) == 6
    assert continents[0].code == "AF"
    assert continents[0].name == "Africa"


def test_reraise_backend_error(country_info_service: SupportsCountryInfo) -> None:
    with pytest.raises(BackendError):
        country_info_service.invalid_operation()
