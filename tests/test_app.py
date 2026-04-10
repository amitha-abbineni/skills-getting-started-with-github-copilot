import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Fresh activities fixture with 3 sample activities
        Act: Make GET request to /activities
        Assert: Response has 200 status and contains all activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_has_correct_structure(self, client, fresh_activities):
        """
        Test that returned activities have the correct data structure.
        
        Arrange: Fresh activities fixture
        Act: Make GET request to /activities
        Assert: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_succeeds(self, client, fresh_activities):
        """
        Test that a new participant can successfully sign up for an activity.
        
        Arrange: Fresh activities with Chess Club having 2 existing participants
        Act: Sign up a new participant
        Assert: Response is 200, participant is added to list
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newuser@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_participant_fails(self, client, fresh_activities):
        """
        Test that a participant already signed up cannot sign up again.
        
        Arrange: Fresh activities with existing participant
        Act: Try to sign up the same participant again
        Assert: Response is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Test that signing up for a non-existent activity fails.
        
        Arrange: Fresh activities (no "Dancing Club")
        Act: Try to sign up for non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Dancing Club"
        email = "user@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_succeeds(self, client, fresh_activities):
        """
        Test that an existing participant can be unregistered successfully.
        
        Arrange: Fresh activities with Chess Club having 2 participants
        Act: Unregister one participant
        Assert: Response is 200, participant is removed from list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
        assert email_to_remove not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonregistered_participant_fails(self, client, fresh_activities):
        """
        Test that unregistering a participant not in the activity fails.
        
        Arrange: Fresh activities with Chess Club
        Act: Try to unregister a participant not registered
        Assert: Response is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email_not_registered = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_not_registered}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_from_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Test that unregistering from a non-existent activity fails.
        
        Arrange: Fresh activities (no "Dancing Club")
        Act: Try to unregister from non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Dancing Club"
        email = "user@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_last_participant(self, client, fresh_activities):
        """
        Test that unregistering the last participant works correctly.
        
        Arrange: Fresh activities with Gym Class having 2 participants
        Act: Unregister one participant
        Assert: Activity's participants list is updated
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
