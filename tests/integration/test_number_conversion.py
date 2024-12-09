from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Literal, Protocol, Union

import pytest
from pydantic import BaseModel, Field, HttpUrl, RootModel
from typing_extensions import assert_type
from zeep import AsyncClient, Client

from combadge.core.response import ErrorResponse, SuccessfulResponse
from combadge.support.common import Body
from combadge.support.http.request import Payload
from combadge.support.soap.markers import operation_name
from combadge.support.soap.response import BaseSoapFault
from combadge.support.zeep.backends.async_ import ZeepBackend as AsyncZeepBackend
from combadge.support.zeep.backends.base import ByBindingName, ByServiceName
from combadge.support.zeep.backends.sync import ZeepBackend as SyncZeepBackend


class NumberToWordsRequest(BaseModel, populate_by_name=True):
    number: Annotated[int, Field(alias="ubiNum")]


class NumberToWordsResponse(RootModel, SuccessfulResponse):
    root: str


class NumberTooLargeResponse(RootModel, ErrorResponse):
    root: Literal["number too large"]


class _TestFault(BaseSoapFault):  # type: ignore[override]
    code: Literal["SOAP-ENV:Server"]
    message: Literal["Test Fault"]


class SupportsNumberConversion(Protocol):
    @operation_name("NumberToWords")
    @abstractmethod
    def number_to_words(
        self,
        request: Annotated[NumberToWordsRequest, Payload(by_alias=True)],
    ) -> Union[Body[Union[NumberTooLargeResponse, NumberToWordsResponse]], _TestFault]:
        raise NotImplementedError


class SupportsNumberConversionAsync(Protocol):
    @operation_name("NumberToWords")
    @abstractmethod
    async def number_to_words(
        self,
        request: Annotated[NumberToWordsRequest, Payload(by_alias=True)],
    ) -> Union[Body[Union[NumberTooLargeResponse, NumberToWordsResponse]], _TestFault]:
        raise NotImplementedError


@pytest.fixture
def number_conversion_service() -> Iterable[SupportsNumberConversion]:
    with Client(
        wsdl=str(Path(__file__).parent / "wsdl" / "NumberConversion.wsdl"),
        port_name="NumberConversionSoap",
    ) as client:
        yield SyncZeepBackend(client.service)[SupportsNumberConversion]  # type: ignore[type-abstract]


@pytest.fixture
def number_conversion_service_async() -> Iterable[SupportsNumberConversionAsync]:
    with AsyncClient(
        wsdl=str(Path(__file__).parent / "wsdl" / "NumberConversion.wsdl"),
        port_name="NumberConversionSoap",
    ) as client:
        yield AsyncZeepBackend(client.service)[SupportsNumberConversionAsync]  # type: ignore[type-abstract]


@pytest.mark.vcr(decode_compressed_response=True)
def test_happy_path_scalar_response(number_conversion_service: SupportsNumberConversion) -> None:
    response = number_conversion_service.number_to_words(NumberToWordsRequest(number=42))
    assert response.unwrap().root == "forty two "


@pytest.mark.vcr(decode_compressed_response=True)
def test_sad_path_scalar_response(number_conversion_service: SupportsNumberConversion) -> None:
    response = number_conversion_service.number_to_words(NumberToWordsRequest(number=-1))

    with pytest.raises(NumberTooLargeResponse.Error) as exception:
        response.raise_for_result()
    assert exception.value.response == response


@pytest.mark.vcr(decode_compressed_response=True)
def test_sad_path_web_fault(number_conversion_service: SupportsNumberConversion) -> None:
    # Note: the cassette is manually patched to return the SOAP fault.
    response = number_conversion_service.number_to_words(NumberToWordsRequest(number=42))
    with pytest.raises(_TestFault.Error):
        response.raise_for_result()


@pytest.mark.vcr
async def test_happy_path_scalar_response_async(number_conversion_service_async: SupportsNumberConversionAsync) -> None:
    response = await number_conversion_service_async.number_to_words(NumberToWordsRequest(number=42))
    assert_type(response, Union[NumberToWordsResponse, NumberTooLargeResponse, _TestFault])

    response = response.unwrap()
    assert_type(response, NumberToWordsResponse)

    assert response.root == "forty two "


@pytest.mark.vcr
@pytest.mark.parametrize(
    "service",
    [
        ByServiceName(port_name="NumberConversionSoap"),
        ByBindingName(
            binding_name="{http://www.dataaccess.com/webservicesserver/}NumberConversionSoapBinding",
            address=HttpUrl(
                "https://www.dataaccess.com/webservicesserver/NumberConversion.wso",
            ),
        ),
    ],
)
def test_happy_path_with_params_sync(service: Union[ByServiceName, ByBindingName]) -> None:
    backend = SyncZeepBackend.with_params(
        Path(__file__).parent / "wsdl" / "NumberConversion.wsdl",
        service=service,
        operation_timeout=1,
    )
    service = backend[SupportsNumberConversion]  # type: ignore[type-abstract]
    response = service.number_to_words(NumberToWordsRequest(number=42)).unwrap()
    assert response.root == "forty two "


@pytest.mark.vcr
@pytest.mark.parametrize(
    "service",
    [
        ByServiceName(port_name="NumberConversionSoap"),
        ByBindingName(
            binding_name="{http://www.dataaccess.com/webservicesserver/}NumberConversionSoapBinding",
            address=HttpUrl(
                "https://www.dataaccess.com/webservicesserver/NumberConversion.wso",
            ),
        ),
    ],
)
async def test_happy_path_with_params_async(service: Union[ByServiceName, ByBindingName]) -> None:
    backend = AsyncZeepBackend.with_params(
        Path(__file__).parent / "wsdl" / "NumberConversion.wsdl",
        service=service,
        operation_timeout=1,
    )
    service = backend[SupportsNumberConversionAsync]  # type: ignore[type-abstract]
    response = (await service.number_to_words(NumberToWordsRequest(number=42))).unwrap()
    assert response.root == "forty two "
