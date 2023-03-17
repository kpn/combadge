from abc import abstractmethod
from pathlib import Path
from typing import Iterable, List

from pydantic import BaseModel, Field
from pytest import fixture, mark
from typing_extensions import Annotated, Protocol
from zeep import Client

from combadge.core.interfaces import SupportsService
from combadge.core.response import SuccessfulResponse
from combadge.support.soap.markers import Body, operation_name
from combadge.support.zeep.backends.sync import ZeepBackend


class CountryInfoRequest(BaseModel):
    """The service method takes no parameters."""


class Continent(BaseModel):
    code: Annotated[str, Field(alias="sCode")]
    name: Annotated[str, Field(alias="sName")]


class CountryInfoResponse(SuccessfulResponse):
    __root__: List[Continent]


class SupportsCountryInfo(SupportsService, Protocol):
    @operation_name("ListOfContinentsByName")
    @abstractmethod
    def list_of_continents_by_name(self, request: Body[CountryInfoRequest]) -> CountryInfoResponse:
        raise NotImplementedError


@fixture
def country_info_service() -> Iterable[SupportsCountryInfo]:
    with Client(wsdl=str(Path(__file__).parent / "wsdl" / "CountryInfoService.wsdl")) as client:
        yield SupportsCountryInfo.bind(ZeepBackend(client.service))


@mark.vcr(decode_compressed_response=True)
def test_happy_path(country_info_service: SupportsCountryInfo) -> None:
    response = country_info_service.list_of_continents_by_name(CountryInfoRequest())

    continents = response.unwrap().__root__
    assert isinstance(continents, list)
    assert len(continents) == 6
    assert continents[0].code == "AF"
    assert continents[0].name == "Africa"
