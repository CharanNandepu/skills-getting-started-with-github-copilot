"""
Tests for the Mergington High School Activities API

Using the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to original state before each test"""
    from src.app import activities
    
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
        "Soccer Team": {
            "description": "Practice teamwork and compete in soccer matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "nina@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Improve basketball skills and play friendly games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["tyler@mergington.edu", "maya@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stagecraft, and prepare for school productions",
            "schedule": "Thursdays, 3:45 PM - 5:15 PM",
            "max_participants": 20,
            "participants": ["oliver@mergington.edu", "sophia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 14,
            "participants": ["aiden@mergington.edu", "zoe@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    activities.clear()
    activities.update(original)
    yield
    activities.clear()
    activities.update(original)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that all activities are returned"""
        # Arrange
        expected_activity_count = 9
        expected_activities = ["Chess Club", "Programming Class"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert all(activity in data for activity in expected_activities)

    def test_get_activities_has_required_fields(self, reset_activities):
        """Test that activities have all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, reset_activities):
        """Test successful signup returns success message"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert f"Signed up {email} for {activity_name}" in data["message"]

    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_fails(self, reset_activities):
        """Test that signup fails when participant is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signup fails for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_successful(self, reset_activities):
        """Test successful unregistration returns success message"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert f"Unregistered {email} from {activity_name}" in data["message"]

    def test_unregister_removes_participant_from_activity(self, reset_activities):
        """Test that unregister actually removes the participant from the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up_fails(self, reset_activities):
        """Test that unregister fails when participant is not signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregister fails for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_then_unregister(self, reset_activities):
        """Test complete workflow: sign up and then unregister"""
        # Arrange
        email = "integration@mergington.edu"
        activity = "Chess Club"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert - Signup successful
        assert signup_response.status_code == 200

        # Act - Verify signup
        get_response = client.get("/activities")
        activities = get_response.json()

        # Assert - Participant added
        assert email in activities[activity]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert - Unregister successful
        assert unregister_response.status_code == 200

        # Act - Verify unregister
        final_response = client.get("/activities")
        final_activities = final_response.json()

        # Assert - Participant removed
        assert email not in final_activities[activity]["participants"]

    def test_multiple_signups(self, reset_activities):
        """Test multiple participants signing up for the same activity"""
        # Arrange
        activity = "Chess Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]

        # Act - Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200

        # Act - Fetch activities
        response = client.get("/activities")
        activities = response.json()

        # Assert - All students are signed up
        for email in emails:
            assert email in activities[activity]["participants"]
