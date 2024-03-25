import json
import os

from login.models import OsmUser
from core.models import Dataset
from rest_framework import status
from rest_framework.test import APILiveServerTestCase, RequestsClient
from model_bakery import baker

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


def generate_payload(id, osm_user):
    """Generate JSON payload for HTTP POST at /model"""
    dataset = baker.make(
        Dataset, 
        name = f"Test Dataset {id}",
        source_imagery = "http://example.com",
        status = 1,
        created_by=osm_user
    )

    return {
        "name": f"Model {id}",
        "status": 1,
        "dataset": dataset.id
    }



class ModelTest(APILiveServerTestCase):
    """
    Tests for /model/

    Endpoints covered:

    GET /model/
    POST /model/

    GET /model/:id
    # PUT /model/:id
    PATCH /model/:id
    DELETE /model/:id

    """

    def setUp(self):
        self.osm_user = baker.make(OsmUser, osm_id="12948", username="testUser")
        self.client = RequestsClient()

    def test_model_create_and_delete(self):
        """Create a Model object then DELETE it."""

        payload = generate_payload(1, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/model/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.delete(f"{API_BASE}/model/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_model_create_and_list(self):
        """Create a Model object then GET all Model objects."""

        payload = generate_payload(2, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/model/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(f"{API_BASE}/model/", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        
    def test_model_create_and_partial_update(self):
        """Create a Model object then update it using a PATCH request."""

        payload_one = generate_payload(3, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/model/", json.dumps(payload_one), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        payload_two = payload_one
        payload_two["status"] = 0

        res = self.client.patch(
            f"{API_BASE}/model/{id}",
            json.dumps(payload_two),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_model_create_and_read(self):
        """Create a Model object then GET that object by id."""

        payload = generate_payload(4, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/model/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        first = res.json()
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/model/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second = res.json()

        self.assertEqual(first, second)
