import asyncio
import functools

from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from sync_client_lib.client import ApiClient, ApiEndpointCollection

P = ParamSpec("P")
R = TypeVar("R")

SyncFunc = Callable[P, R]
CoroFunc = Callable[P, Coroutine[Any, Any, R]]
CoroRetFunc = Callable[P, Coroutine[Any, Any, R]]
CoroFuncWrapper = Callable[[SyncFunc[P, R]], CoroFunc[P, R]]


def _typehint_coroutine() -> CoroFuncWrapper[P, R]:
    """Decorate a function's typehint to return its normal value wrapped in a coro."""

    def outer(fn: SyncFunc[P, R]) -> CoroRetFunc[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return outer


class AsyncApiEndpointProxy:
    _method: Callable
    _convert_async: bool

    def __init__(self, method: Callable, convert_async: bool):
        self._method = method
        self._convert_async = convert_async

    async def __call__(self, *args, **kwargs):
        if self._convert_async:
            return await asyncio.get_event_loop().run_in_executor(
                None, functools.partial(self._method, *args, **kwargs)
            )
        else:
            return self._method(*args, **kwargs)


class AsyncApiEndpointCollectionProxy:
    _collection: ApiEndpointCollection

    def __init__(self, collection: ApiEndpointCollection):
        self._collection = collection

    def __getattr__(self, name: str):
        convert_async = name.endswith("_async")

        return AsyncApiEndpointProxy(
            getattr(
                self._collection,
                name[:-6] if convert_async else name,
                convert_async,
            )
        )


class AsyncApiEndpointCollection(ApiEndpointCollection):
    retrieve_resource_async = _typehint_coroutine()(
        ApiEndpointCollection.retrieve_resource
    )


class AsyncApiClientProxy:
    _client: ApiClient

    endpoints: AsyncApiEndpointCollection

    def __init__(self):
        self._client = ApiClient()

    def __getattr__(self, name: str):
        return AsyncApiEndpointCollectionProxy(getattr(self._client, name))


if __name__ == "__main__":
    client = AsyncApiClientProxy()

    print(asyncio.run(client.endpoints.retrieve_resource(43)))

    print(asyncio.run(client.endpoints.retrieve_resource_async(43)))
