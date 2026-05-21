import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.base_page import BasePage
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage
from tests.pages.profile_page import ProfilePage
from tests.pages.tasks_page import TaskDetailPage, TasksPage
from tests.pages.tasks_page import TaskFormPage
from selenium.common.exceptions import NoAlertPresentException

class TestNegative:

    @pytest.mark.negative
    def test_xss_attempt(self, tasks_page: TasksPage, task_detail: TaskDetailPage, task_form: TaskFormPage):
        payload_title="<script>alert(1)</script>"

        tasks_page.open()
        task_id = tasks_page.get_task_id(0)
        tasks_page.click_task_by_id(task_id)
        task_detail.edit()
        task_form.fill(title=payload_title)
        task_form.submit()
        tasks_page.click_task_by_id(task_id)
        details = task_detail.get_details()
        assert details["title"] == payload_title

        try:
            tasks_page.driver.switch_to.alert
            assert False, "XSS alert was executed"
        except NoAlertPresentException:
            pass
        

    #- [ ] Very long title (500 chars) — verify it is truncated or rejected cleanly, no 500 error
    @pytest.mark.negative
    def test_long_title(self, admin_api, base_url):
        test_data = {
            "title": "A" * 500,
            "priority": "MEDIUM",
            "status": "TODO",
            "category": "Testing",
        }
        r = admin_api.post(f"{base_url}/api/tasks", json=test_data)
        assert r.status_code != 500
    
    #- [ ] Special characters in search — `& % # @ !` — server must return 200 not 500
    @pytest.mark.negative
    def test_search_special_characters(self, admin_api, base_url):
        r = admin_api.get(f"{base_url}/api/tasks", params={"search": "& % # @ !"})
        assert r.status_code == 200

    # - [ ] Create task with past due date — assert it is accepted (or rejected with a clear error, not a crash)

    @pytest.mark.negative
    def test_past_due_date(self, admin_api, base_url):
        r = admin_api.post(f"{base_url}/api/tasks", json={
            "title": "Past due task",
            "priority": "LOW",
            "status": "TODO",
            "category": "Testing",
            "dueDate": "2020-01-01"
        })
        assert r.status_code in [200, 201, 400]

    @pytest.mark.negative
    #- [ ] Concurrent rapid clicks on Delete — click Delete button twice in quick succession, assert only one request is made (check task count)
    def test_concurrent_delete(self, tasks_page: TasksPage, task_detail: TaskDetailPage):

        tasks_page.open()
        task_count_before = tasks_page.get_task_count()
        task_id = tasks_page.get_task_id(0)
        tasks_page.click_task_by_id(task_id)
        task_detail.delete_task_press_twice()
        tasks_count_after = tasks_page.get_task_count()

        assert task_count_before == tasks_count_after + 1