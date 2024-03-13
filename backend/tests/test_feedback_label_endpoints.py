from core.models import Dataset, Model, Training, FeedbackAOI

from django.contrib.gis.geos import Polygon
from login.models import OsmUser

import json
import os

from rest_framework import status
from rest_framework.test import APILiveServerTestCase, RequestsClient

API_BASE = "http://0.0.0.0:8000/api/v1"

headersList = {
    "accept": "application/json",
    "access-token": os.environ.get("TESTING_TOKEN"),
}

json_type_header = {
    "accept": "application/json",
    "access-token": os.environ.get("TESTING_TOKEN"),
    "content-type": "application/json",
}


def generate_payload(feedback_aoi_id, model, osm_user):
    """Generate JSON payload for HTTP POST at /feedback-label"""

    training = Training.objects.create(
        model=model,
        zoom_level=[19, 20, 21, 22],
        created_by=osm_user,
        epochs=10,
        batch_size=32,
    )

    FeedbackAOI.objects.create(
        user=osm_user,
        training=training,
        source_imagery="http://example.com/aoi_image.png",
        geom=Polygon(
            ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)),
            ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4), (0.4, 0.4)),
        ),
    )

    return {
        "osm_id": 12948,
        "tags": {"testing": "testing"},
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
        "feedback_aoi": feedback_aoi_id,
    }


class FeedbackLabelTest(APILiveServerTestCase):
    """
    Tests for /feedback-label/

    Endpoints covered:

    GET /feedback-label/
    POST /feedback-label/

    GET /feedback-label/:id
    PATCH /feedback-label/:id
    DELETE /feedback-label/:id

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

    def test_feedback_label_create_and_delete(self):
        """Create a FeedbackLabel object then DELETE it."""
        payload = generate_payload(1, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-label/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.delete(f"{API_BASE}/feedback-label/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_feedback_label_create_and_list(self):
        """Create a FeedbackLabel object then GET all FeedbackLabel objects."""
        payload = generate_payload(2, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-label/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(f"{API_BASE}/feedback-label/", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_label_create_and_partial_update(self):
        """Create a FeedbackAOI object then update it."""

        payload_one = generate_payload(3, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-label/",
            json.dumps(payload_one),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        payload_two = payload_one
        payload_two["tags"] = {"testing": "testing222"}
        payload_two["geom"]["coordinates"][0][2] = [
            32.588869114643053,
            0.348171660921362,
        ]

        res = self.client.patch(
            f"{API_BASE}/feedback-label/{id}",
            json.dumps(payload_two),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_label_create_and_read(self):
        """Create a FeedbackLabel object then GET that object by id."""

        payload = generate_payload(4, self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback-label/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        first = res.json()
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/feedback-label/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second = res.json()

        self.assertEqual(first, second)
