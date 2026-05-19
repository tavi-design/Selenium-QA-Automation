"""
API test suite — direct HTTP tests using requests (no browser).

PARTIALLY IMPLEMENTED. Complete the TODOs marked with TICKET numbers.
"""
import pytest



# ── Auth API ──────────────────────────────────────────────────────────────────

class TestAuthAPI:

    @pytest.mark.api
    def test_login_valid_admin(self, api_session, base_url):
        r = api_session.post(f"{base_url}/api/auth/login",
                             json={"username": "admin", "password": "admin123"})
        assert r.status_code == 200
        assert r.json()["user"]["username"] == "admin"

    @pytest.mark.api
    def test_login_returns_user_object(self, api_session, base_url):
        r = api_session.post(f"{base_url}/api/auth/login",
                             json={"username": "admin", "password": "admin123"})
        user = r.json()["user"]
        assert {"username", "name", "email", "role"} <= user.keys()

    @pytest.mark.api
    def test_login_wrong_password_returns_401(self, api_session, base_url):
        r = api_session.post(f"{base_url}/api/auth/login",
                             json={"username": "admin", "password": "wrong"})
        assert r.status_code == 401

    @pytest.mark.api
    def test_login_unknown_user_returns_401(self, api_session, base_url):
        r = api_session.post(f"{base_url}/api/auth/login",
                             json={"username": "ghost", "password": "x"})
        assert r.status_code == 401

    @pytest.mark.api
    def test_me_authenticated(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/auth/me")
        assert r.status_code == 200
        assert r.json()["username"] == "admin"

    @pytest.mark.api
    def test_me_unauthenticated_returns_401(self, api_session, base_url):
        r = api_session.get(f"{base_url}/api/auth/me")
        assert r.status_code == 401

    @pytest.mark.api
    @pytest.mark.parametrize("login_details", [
        {"username" : "", "password" : ""}, 
        {"username" : "a", "password" : ""},
        {"username" : "user", "password" : "wrong"},
        {"username" : "A", "password" : "user123"},
        ])
    def test_invalid_login(self, api_session, base_url, login_details):
        r = api_session.post(f"{base_url}/api/auth/login", 
                               json=login_details)
        assert r.status_code == 401

# ── Tasks API ─────────────────────────────────────────────────────────────────

class TestTasksAPI:

    @pytest.mark.api
    def test_get_tasks_returns_paginated_response(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/tasks")
        assert r.status_code == 200
        body = r.json()
        assert {"data", "total", "page", "totalPages", "perPage"} <= body.keys()

    @pytest.mark.api
    def test_get_tasks_default_page_size_is_10(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/tasks")
        assert len(r.json()["data"]) == 10

    @pytest.mark.api
    def test_get_tasks_unauthenticated_returns_401(self, api_session, base_url):
        r = api_session.get(f"{base_url}/api/tasks")
        assert r.status_code == 401

    @pytest.mark.api
    def test_create_task_returns_201(self, admin_api, base_url):
        payload = {
            "title": "API test task",
            "priority": "MEDIUM",
            "status": "TODO",
            "category": "Testing",
        }
        r = admin_api.post(f"{base_url}/api/tasks", json=payload)
        assert r.status_code == 201
        task = r.json()
        assert task["title"] == "API test task"
        assert "id" in task
    
    @pytest.mark.api
    def test_created_task_has_expected_schema(self, admin_api, base_url):
        payload = {"title": "Schema check", "priority": "LOW", "status": "TODO", "category": "Bug"}
        task = admin_api.post(f"{base_url}/api/tasks", json=payload).json()
        required_keys = {"id", "title", "description", "priority", "status", "category", "assignee", "dueDate", "createdAt"}
        assert required_keys <= task.keys()

    @pytest.mark.api
    def test_create_task_missing_title_returns_400(self, admin_api, base_url):
        r = admin_api.post(f"{base_url}/api/tasks",
                           json={"priority": "LOW", "status": "TODO", "category": "Bug"})
        assert r.status_code == 400

    @pytest.mark.api
    def test_get_task_by_id(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/tasks/1")
        assert r.status_code == 200
        assert r.json()["id"] == 1

    @pytest.mark.api
    def test_get_task_not_found_returns_404(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/tasks/99999")
        assert r.status_code == 404

    @pytest.mark.api
    def test_delete_task(self, admin_api, base_url):
        task = admin_api.post(f"{base_url}/api/tasks",
                              json={"title": "To delete", "priority": "LOW",
                                    "status": "TODO", "category": "Testing"}).json()
        r = admin_api.delete(f"{base_url}/api/tasks/{task['id']}")
        assert r.status_code == 204

    @pytest.mark.api
    def test_delete_nonexistent_returns_404(self, admin_api, base_url):
        r = admin_api.delete(f"{base_url}/api/tasks/99999")
        assert r.status_code == 404

    @pytest.mark.api
    def test_search_filter_returns_matching_tasks(self, admin_api, base_url):
        response = admin_api.get(f"{base_url}/api/tasks?search=login")
        body = response.json()
        tasks = body["data"]
        assert len(tasks) > 0
        for task in tasks:
            title = task["title"].lower()
            description = task["description"].lower()
            assert "login" in title or "login" in description
    

    @pytest.mark.api
    def test_priority_filter(self, admin_api, base_url):
        response = admin_api.get(f"{base_url}/api/tasks?priority=CRITICAL")
        body = response.json()
        tasks = body["data"]
        if len(tasks) > 0:
            for task in tasks:
                priority = task["priority"]
                assert priority == "CRITICAL"


    @pytest.mark.api
    def test_pagination_page_2_different_from_page_1(self, admin_api, base_url):
        tasks_first = admin_api.get(f"{base_url}/api/tasks?page=1").json()["data"]
        tasks_second = admin_api.get(f"{base_url}/api/tasks?page=2").json()["data"]
        assert len(tasks_first) > 0 and len(tasks_second) > 0
        ids_first = [task["id"] for task in tasks_first]
        ids_second = [task["id"] for task in tasks_second]
        assert set(ids_first).isdisjoint(ids_second)

    @pytest.mark.api
    def test_update_task_returns_updated_fields(self, admin_api, base_url):
        changed_title = "changed title"
        response = admin_api.put(f"{base_url}/api/tasks/1",
                                json={"title" : changed_title})
        assert response.status_code == 200
        body = response.json()
        assert body["title"] == changed_title
        

    @pytest.mark.api
    def test_update_task_invalid_priority_returns_400(self, admin_api, base_url):
        incorrect_priority = "WrongPRIORITY"
        response = admin_api.put(f"{base_url}/api/tasks/1",
                                 json={"priority" : incorrect_priority })
        assert response.status_code == 400


# ── Stats API ─────────────────────────────────────────────────────────────────

class TestStatsAPI:
    @pytest.mark.api
    def test_stats_returns_expected_keys(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/stats")
        assert r.status_code == 200
        keys = {"total", "todo", "inProgress", "done", "blocked", "overdue", "critical"}
        assert keys <= r.json().keys()

    @pytest.mark.api
    def test_stats_total_matches_task_count(self, admin_api, base_url):
        stats  = admin_api.get(f"{base_url}/api/stats").json()
        tasks  = admin_api.get(f"{base_url}/api/tasks?page=1").json()
        assert stats["total"] == tasks["total"]
        

    @pytest.mark.api
    def test_stats_values_are_non_negative_integers(self, admin_api, base_url):
        response = admin_api.get(f"{base_url}/api/stats")
        assert response.status_code == 200
        stats = response.json()
        assert all (v >= 0 for v in stats.values())

    @pytest.mark.api
    def test_stats_unauthenticated_returns_401(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/stats")
        assert response.status_code == 401
