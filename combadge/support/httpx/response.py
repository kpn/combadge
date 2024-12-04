from combadge.support.common.response import ResponseBodyMixinDict
from combadge.support.http.response import HttpResponseMixinDict


class ResponseDict(ResponseBodyMixinDict, HttpResponseMixinDict):
    """HTTPX backend response dictionary."""
