from abc import abstractmethod
from pathlib import Path
from typing import Iterable, Union

from pydantic import BaseModel, Field
from pytest import fixture, mark, raises
from typing_extensions import Annotated, Literal, Protocol, assert_type
from zeep import AsyncClient, Client

from combadge.core.interfaces import SupportsService
from combadge.core.response import ErrorResponse, SuccessfulResponse
from combadge.support.soap.markers import Body, operation_name
from combadge.support.zeep.backends.async_ import ZeepBackend as AsyncZeepBackend
from combadge.support.zeep.backends.sync import ZeepBackend as SyncZeepBackend


class NumberToWordsRequest(BaseModel, allow_population_by_field_name=True):
    number: Annotated[int, Field(alias="ubiNum")]


class NumberToWordsResponse(SuccessfulResponse):
    __root__: str


class NumberTooLargeResponse(ErrorResponse):
    __root__: Literal["number too large"]


class SupportsNumberConversion(SupportsService, Protocol):
    @operation_name("NumberToWords")
    @abstractmethod
    def number_to_words(
        self,
        request: Body[NumberToWordsRequest],
    ) -> Union[NumberTooLargeResponse, NumberToWordsResponse]:
        raise NotImplementedError


class SupportsNumberConversionAsync(SupportsService, Protocol):
    @operation_name("NumberToWords")
    @abstractmethod
    async def number_to_words(
        self,
        request: Body[NumberToWordsRequest],
    ) -> Union[NumberTooLargeResponse, NumberToWordsResponse]:
        raise NotImplementedError


@fixture
def number_conversion_service() -> Iterable[SupportsNumberConversion]:
    with Client(
        wsdl=str(Path(__file__).parent / "wsdl" / "NumberConversion.wsdl"),
        port_name="NumberConversionSoap",
    ) as client:
        yield SupportsNumberConversion.bind(SyncZeepBackend(client.service))


@fixture
def number_conversion_service_async() -> Iterable[SupportsNumberConversionAsync]:
    with AsyncClient(
        wsdl=str(Path(__file__).parent / "wsdl" / "NumberConversion.wsdl"),
        port_name="NumberConversionSoap",
    ) as client:
        yield SupportsNumberConversionAsync.bind(AsyncZeepBackend(client.service))


@mark.vcr(decode_compressed_response=True)
def test_happy_path_scalar_response(number_conversion_service: SupportsNumberConversion) -> None:
    response = number_conversion_service.number_to_words(NumberToWordsRequest(number=42))
    assert response.unwrap().__root__ == "forty two "


@mark.vcr(decode_compressed_response=True)
def test_sad_path_scalar_response(number_conversion_service: SupportsNumberConversion) -> None:
    response = number_conversion_service.number_to_words(NumberToWordsRequest(number=-1))

    with raises(NumberTooLargeResponse.Error) as exception:
        response.raise_for_result()
    assert exception.value.response == response


@mark.vcr
async def test_happy_path_scalar_response_async(number_conversion_service_async: SupportsNumberConversionAsync) -> None:
    response = await number_conversion_service_async.number_to_words(NumberToWordsRequest(number=42))
    assert_type(response, Union[NumberToWordsResponse, NumberTooLargeResponse])

    response = response.unwrap()
    assert_type(response, NumberToWordsResponse)

    assert response.__root__ == "forty two "
