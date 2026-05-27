def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) >= 1

    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_success_adds_participant(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    updated_activities = client.get("/activities").json()
    assert email in updated_activities[activity_name]["participants"]


def test_signup_returns_404_for_missing_activity(client):
    response = client.post(
        "/activities/Nonexistent Activity/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_when_activity_is_full(client):
    activity_name = "Debate Team"
    activities_data = client.get("/activities").json()
    max_participants = activities_data[activity_name]["max_participants"]

    for index in range(max_participants):
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"filler{index}@mergington.edu"},
        )

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": "overflow@mergington.edu"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_success_removes_participant(client):
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    updated_activities = client.get("/activities").json()
    assert email not in updated_activities[activity_name]["participants"]


def test_unregister_returns_404_for_missing_activity(client):
    response = client.delete(
        "/activities/Nonexistent Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_non_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not-in-club@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"