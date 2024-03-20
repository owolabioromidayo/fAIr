from django.contrib.gis.geos import Polygon
from login.models import OsmUser

import json
import os

from rest_framework import status
from rest_framework.test import APILiveServerTestCase, RequestsClient

API_BASE = "http://testserver/api/v1"

headersList = {
    "accept": "application/json",
    "access-token": os.environ.get("TESTING_TOKEN"),
}

json_type_header = {
    "accept": "application/json",
    "access-token": os.environ.get("TESTING_TOKEN"),
    "content-type": "application/json",
}


def generate_payload(id):
    """Generate JSON payload for HTTP POST at /dataset"""

    return {
        "name": f"Test Dataset {id}",
        "source_imagery": "http://example.com",
        "status": 1
    }


class DatasetTest(APILiveServerTestCase):
    """
    Tests for /dataset/

    Endpoints covered:

    GET /dataset/
    POST /dataset/

    GET /dataset/:id
    PUT /dataset/:id
    PATCH /dataset/:id
    DELETE /dataset/:id

    """

    def setUp(self):
        self.osm_user = OsmUser.objects.create(osm_id="12948", username="testUser")
        self.client = RequestsClient()

    def test_dataset_create_and_delete(self):
        """Create a Dataset object then DELETE it."""

        payload = generate_payload(1)

        res = self.client.post(
            f"{API_BASE}/dataset/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.delete(f"{API_BASE}/dataset/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_dataset_create_and_list(self):
        """Create a Dataset object then GET all Feedback objects."""

        payload = generate_payload(2)

        res = self.client.post(
            f"{API_BASE}/dataset/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(f"{API_BASE}/dataset/", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # def test_dataset_create_and_update(self):
    #     """Create a Dataset object then update it using a PUT request."""

    #     payload_one = generate_payload(3)

    #     res = self.client.post(
    #         f"{API_BASE}/dataset/", json.dumps(payload_one), headers=json_type_header
    #     )

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     id = res.json()["id"]

    #     payload_two = payload_one
    #     payload_two["source_imagery"] = "http://example23323.com"

    #     print(payload_two)

    #     res = self.client.put(
    #         f"{API_BASE}/dataset/{id}",
    #         json.dumps(payload_two),
    #         headers=json_type_header,
    #     )

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_dataset_create_and_partial_update(self):
        """Create a Dataset object then update it using a PATCH request."""

        payload_one = generate_payload(4)

        res = self.client.post(
            f"{API_BASE}/dataset/", json.dumps(payload_one), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        payload_two = payload_one
        payload_two["source_imagery"] = "http://example23323.com"

        res = self.client.patch(
            f"{API_BASE}/dataset/{id}",
            json.dumps(payload_two),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_dataset_create_and_read(self):
        """Create a Dataset object then GET that object by id."""

        payload = generate_payload(5)

        res = self.client.post(
            f"{API_BASE}/dataset/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        first = res.json()
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/dataset/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second = res.json()

        self.assertEqual(first, second)
