from core.models import Dataset, Model, Training, FeedbackAOI

from django.contrib.gis.geos import Polygon
from login.models import OsmUser
from model_bakery import baker

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


def generate_payload(model, osm_user):
    """Generate JSON payload for HTTP POST at /feedback"""

    training = baker.make(
        Training,
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
        "training": training.id,
        "zoom_level": 18,
        "feedback_type": "TP",
    }


class FeedbackTest(APILiveServerTestCase):
    """
    Tests for /feedback/

    Endpoints covered:

    GET /feedback/
    POST /feedback/

    GET /feedback/:id
    PATCH /feedback/:id
    DELETE /feedback/:id

    POST /feedback/training/submit

    """

    def setUp(self):
        self.osm_user = baker.make(OsmUser, osm_id="12948", username="testUser")
        self.dataset = baker.make(
            Dataset,
            name="Test Dataset",
            created_by=self.osm_user,
        )
        self.model = baker.make(
            Model,
            name="Test Model",
            created_by=self.osm_user,
            dataset=self.dataset,
        )

        self.client = RequestsClient()

    def test_feedback_create_and_delete(self):
        """Create a Feedback object then DELETE it."""

        payload = generate_payload(self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        res = self.client.delete(f"{API_BASE}/feedback/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_feedback_create_and_list(self):
        """Create a Feedback object then GET all Feedback objects."""

        payload = generate_payload(self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.get(f"{API_BASE}/feedback/", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_create_and_partial_update(self):
        """Create a Feedback object then update it."""

        payload_one = generate_payload(self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback/", json.dumps(payload_one), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        id = res.json()["id"]

        payload_two = payload_one
        payload_two["feedback_type"] = "ÏN"
        payload_two["zoom_level"] = 20

        res = self.client.patch(
            f"{API_BASE}/feedback/{id}",
            json.dumps(payload_two),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_feedback_create_and_read(self):
        """Create a FeedbackAOI object then GET that object by id."""

        payload = generate_payload(self.model, self.osm_user)

        res = self.client.post(
            f"{API_BASE}/feedback/", json.dumps(payload), headers=json_type_header
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        first = res.json()
        id = res.json()["id"]

        res = self.client.get(f"{API_BASE}/feedback/{id}", headers=headersList)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second = res.json()

        self.assertEqual(first, second)

    def test_feedback_training_submit_create(self):
        """Create a payload and send a POST request to /feedback/training/submit/ ."""

        training = baker.make(
            Training,
            model=self.model,
            zoom_level=[19, 20, 21, 22],
            created_by=self.osm_user,
            epochs=10,
            batch_size=32,
            status="FINISHED",
        )

        baker.make(
            FeedbackAOI, 
            user=self.osm_user,
            training=training,
            source_imagery="http://example.com/aoi_image.png",
            geom=Polygon(
                ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)),
                ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4), (0.4, 0.4)),
            ),
            label_status=1,
        )

        payload = {"training_id": training.id, "epochs": 4, "batch_size": 8, "zoom_level": [20]}

        res = self.client.post(
            f"{API_BASE}/feedback/training/submit/",
            json.dumps(payload),
            headers=json_type_header,
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
