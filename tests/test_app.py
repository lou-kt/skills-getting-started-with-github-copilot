"""Test suite for FastAPI activity management app using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Client is ready
        Act: GET /activities
        Assert: Returns 200 with all activities
        """
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_response_structure(self, client):
        """
        Arrange: Client is ready
        Act: GET /activities
        Assert: Each activity has required fields
        """
        response = client.get("/activities")
        activities = response.json()
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_participants_list(self, client):
        """
        Arrange: Client is ready
        Act: GET /activities
        Assert: Each activity has correct participants structure
        """
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_student(self, client):
        """
        Arrange: Valid activity and new email
        Act: POST /activities/Art Club/signup?email=newstudent@mergington.edu
        Assert: Returns 200 with success message and participant added
        """
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]

    def test_signup_duplicate_student(self, client):
        """
        Arrange: Activity with existing participant
        Act: POST for same email twice
        Assert: Second request returns 400 error
        """
        email = "testdup@mergington.edu"
        client.post("/activities/Drama Workshop/signup", params={"email": email})
        response = client.post(
            "/activities/Drama Workshop/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_invalid_activity(self, client):
        """
        Arrange: Non-existent activity name
        Act: POST /activities/Nonexistent Activity/signup
        Assert: Returns 404 error
        """
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

    def test_signup_returns_success_message(self, client):
        """
        Arrange: Valid signup parameters
        Act: POST /activities/Science Olympiad/signup
        Assert: Returns response with activity name and email
        """
        response = client.post(
            "/activities/Science Olympiad/signup",
            params={"email": "olympiad@mergington.edu"}
        )
        result = response.json()
        assert "Signed up" in result["message"]
        assert "olympiad@mergington.edu" in result["message"]
        assert "Science Olympiad" in result["message"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_existing_participant(self, client):
        """
        Arrange: Activity with existing participant
        Act: DELETE /activities/Chess Club/participants?email=michael@mergington.edu
        Assert: Returns 200 with success message
        """
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Removed" in result["message"]

    def test_remove_nonexistent_participant(self, client):
        """
        Arrange: Activity without specified participant
        Act: DELETE with email not in participants list
        Assert: Returns 404 error
        """
        response = client.delete(
            "/activities/Basketball Club/participants",
            params={"email": "notreal@mergington.edu"}
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

    def test_remove_participant_invalid_activity(self, client):
        """
        Arrange: Non-existent activity
        Act: DELETE /activities/Fake Activity/participants
        Assert: Returns 404 error
        """
        response = client.delete(
            "/activities/Fake Activity/participants",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """
        Arrange: Client is ready
        Act: GET /
        Assert: Redirects (307) to /static/index.html
        """
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_followed(self, client):
        """
        Arrange: Client configured to follow redirects
        Act: GET / with follow_redirects=True
        Assert: Final response is 200
        """
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
