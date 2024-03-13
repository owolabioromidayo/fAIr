import json
import os

from core.models import (
    Dataset,
    Model,
    Training,
)

from login.models import OsmUser
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


def generate_payload(training_id, model, osm_user):
    """Generate JSON payload for HTTP POST at /feedback-aoi"""

    Training.objects.create(
        model=model,
        zoom_level=[19, 20, 21, 22],
        created_by=osm_user,
        epochs=10,
        batch_size=32,
    )

    return {
        "geom": {
            "type": "Polygon",
            "coordinates": [
                [
                    [32.588507094820351, 0.348666499011499],
                    [32.588517512656978, 0.348184682976698],
                    [32.588869114643053, 0.348171660921362],
                    [32.588840465592334, 0.348679521066151],
                    [32.588507094820351, 0.348666499011499],
                ]
            ],
        },
        "source_imagery": "http://example.com",
        "training": training_id,
    }


class FeedbackAOITest(APILiveServerTestCase):
    """
    Tests for /feedback-aoi/

    Endpoints covered:

    GET /feedback-aoi/
    POST /feedback-aoi/

    GET /feedback-aoi/:id
    PATCH /feedback-aoi/:id
    DELETE /feedback-aoi/:id

    GET /feedback-aoi/gpx/:id

    """

    def setUp(self):
        self.osm_user = OsmUser.objects.create(osm_id="12948", username="testUser")
        self.dataset = Dataset.objects.create(
            name="Test Dataset", created_by=self.osm_user
        )

        self.model = Model.objects.create(
            name="Test Model", created_by=self.osm_user, dataset=self.dataset
        )

        self.client = RequestsClient()

    def test_feedback_aoi_create_and_delete(self):
        """Create a Feedback AOI object then DELETE it."""

        payload = generate_payload(1, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-aoi/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.delete(f"{API_BASE}/feedback-aoi/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_feedback_aoi_create_and_gpx_read(self):
        """Create a FeedbackAOI object then send a GET request to /feedback-aoi/gpx/:id ."""

        payload = generate_payload(2, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-aoi/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/feedback-aoi/gpx/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_aoi_create_and_list(self):
        """Create a FeedbackAOI object then GET all FeedbackAOI objects."""

        payload = generate_payload(3, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-aoi/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(f"{API_BASE}/feedback-aoi/", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_aoi_create_and_partial_update(self):
        """Create a FeedbackAOI object then update it."""

        payload_one = generate_payload(4, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-aoi/",
            json.dumps(payload_one),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        payload_two = payload_one
        payload_two["source_imagery"] = "http://example23323.com"
        payload_two["geom"]["coordinates"][0][2] = [
            32.588869114643053,
            0.348171660921362,
        ]

        res = self.client.patch(
            f"{API_BASE}/feedback-aoi/{id}",
            json.dumps(payload_two),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_aoi_create_and_read(self):
        """Create a FeedbackAOI object then GET that object by id."""

        payload = generate_payload(5, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-aoi/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        first = res.json()
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/feedback-aoi/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second = res.json()

        self.assertEqual(first, second)
