import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

ACTIVITY = "Chess Club"
EXISTING_EMAIL = "michael@mergington.edu"
NEW_EMAIL = "new.student@mergington.edu"


@pytest.fixture(autouse=True)
def reset_activities():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_names = set(activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == expected_names


def test_signup_adds_student_to_activity():
    # Arrange
    before = list(activities[ACTIVITY]["participants"])

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    assert activities[ACTIVITY]["participants"] == before + [NEW_EMAIL]


def test_signup_duplicate_returns_400():
    # Arrange
    before = list(activities[ACTIVITY]["participants"])

    # Act
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 400
    assert activities[ACTIVITY]["participants"] == before


def test_signup_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404


def test_unregister_removes_student_from_activity():
    # Arrange
    before = list(activities[ACTIVITY]["participants"])

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/unregister", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 200
    assert activities[ACTIVITY]["participants"] == [p for p in before if p != EXISTING_EMAIL]


def test_unregister_student_not_signed_up_returns_404():
    # Arrange
    before = list(activities[ACTIVITY]["participants"])

    # Act
    response = client.delete(f"/activities/{ACTIVITY}/unregister", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert activities[ACTIVITY]["participants"] == before


def test_unregister_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.delete(f"/activities/{unknown_activity}/unregister", params={"email": EXISTING_EMAIL})

    # Assert
    assert response.status_code == 404
