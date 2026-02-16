import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def restore_activities_state():
    snapshot = copy.deepcopy(activities)

    def _restore():
        activities.clear()
        activities.update(snapshot)

    return _restore


@pytest.fixture(autouse=True)
def reset_activities():
    restore = restore_activities_state()
    yield
    restore()


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def test_signup_adds_participant():
    email = "alex@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate():
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400


def test_unregister_removes_participant():
    email = activities["Chess Club"]["participants"][0]

    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/signup", params={"email": "missing@mergington.edu"}
    )

    assert response.status_code == 404
