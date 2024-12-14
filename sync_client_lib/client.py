import requests

from typing import Any

class ApiEndpointCollection:
    def retrieve_resource(self, resource_id: int) -> dict[str, Any]:
        """
        Retrieve a resource from the API

        :param resource_id: The ID of the resource to retrieve
        """
        return requests.get(f"https://httpbin.org/get?id={resource_id}").json()


class ApiClient:
    endpoints: ApiEndpointCollection

    def __init__(self):
        self.endpoints = ApiEndpointCollection()
