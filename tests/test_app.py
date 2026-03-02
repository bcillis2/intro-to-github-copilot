"""
FastAPI Tests for Mergington High School Activities Management

This module contains comprehensive tests for all endpoints of the FastAPI application,
including tests for successful operations and error cases.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to a clean state before each test.
    This ensures test isolation by making a fresh copy of the initial data.
    """
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and recreational play",
            "schedule": "Wednesdays and Saturdays, 2:30 PM - 4:00 PM",
            "max_participants": 10,
            "participants": ["laura@mergington.edu", "marcus@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions and acting workshops",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["sophie@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and STEM exploration",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities for this test
    activities.clear()
    activities.update(original)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original)


# ===========================
# GET /activities Tests
# ===========================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all available activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that all expected activities are present
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Science Club" in data
    assert len(data) == 9  # Should have 9 activities


def test_get_activities_response_structure(client):
    """Test that activity objects have correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    activity = data["Chess Club"]
    
    # Verify required fields are present
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    
    # Verify types
    assert isinstance(activity["description"], str)
    assert isinstance(activity["schedule"], str)
    assert isinstance(activity["max_participants"], int)
    assert isinstance(activity["participants"], list)


def test_get_activities_includes_participants(client):
    """Test that activities include current participants"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    
    # Chess Club should have participants from initial data
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


# ===========================
# POST /activities/{activity_name}/signup Tests
# ===========================

def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds the participant to the activity list"""
    # Signup a new student
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    # Get activities and verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    assert len(data["Chess Club"]["participants"]) == 3


def test_signup_duplicate_registration_fails(client):
    """Test that a student cannot signup twice for the same activity"""
    # Try to signup someone who is already registered
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity_returns_404(client):
    """Test that signup fails for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_multiple_students(client):
    """Test that multiple students can signup for the same activity"""
    # First student
    response1 = client.post(
        "/activities/Programming Class/signup",
        params={"email": "student1@mergington.edu"}
    )
    assert response1.status_code == 200
    
    # Second student
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": "student2@mergington.edu"}
    )
    assert response2.status_code == 200
    
    # Verify both were added
    response = client.get("/activities")
    data = response.json()
    assert "student1@mergington.edu" in data["Programming Class"]["participants"]
    assert "student2@mergington.edu" in data["Programming Class"]["participants"]
    assert len(data["Programming Class"]["participants"]) == 4


# ===========================
# DELETE /activities/{activity_name}/unregister Tests
# ===========================

def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant from the activity list"""
    # Unregister a participant
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    # Get activities and verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    assert len(data["Chess Club"]["participants"]) == 1


def test_unregister_not_signed_up_fails(client):
    """Test that unregistering a non-participant fails"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity_returns_404(client):
    """Test that unregister fails for non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_twice_fails(client):
    """Test that unregistering the same student twice fails"""
    # First unregister should succeed
    response1 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response2.status_code == 400
    assert "not signed up" in response2.json()["detail"]


# ===========================
# Integration Tests
# ===========================

def test_signup_then_unregister_workflow(client):
    """Test a complete workflow of signing up and then unregistering"""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify signup
    response = client.get("/activities")
    assert len(response.json()[activity]["participants"]) == initial_count + 1
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregister
    response = client.get("/activities")
    assert len(response.json()[activity]["participants"]) == initial_count


def test_cannot_exceed_max_participants_still_allows_signup(client):
    """
    Test that signup doesn't reject based on max_participants limit.
    Note: Current implementation doesn't enforce max_participants,
    so this test documents current behavior.
    """
    # Tennis Club has max 10, currently has 2 participants
    for i in range(20):
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": f"student{i}@mergington.edu"}
        )
        assert response.status_code == 200
    
    # Verify all were added (max_participants not enforced)
    response = client.get("/activities")
    tennis_club = response.json()["Tennis Club"]
    assert len(tennis_club["participants"]) == 22  # 2 original + 20 new
