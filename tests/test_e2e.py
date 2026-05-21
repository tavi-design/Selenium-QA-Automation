"""
End-to-end user journey tests.

ONE COMPLETE JOURNEY is implemented as a reference.
Your job: implement the remaining journeys (see TASKS.md TICKET-7).
"""
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


@pytest.mark.e2e
class TestFullUserJourney:

    def test_login_view_dashboard_navigate_to_tasks_and_logout(
        self, driver, base_url
    ):
        """
        Happy-path smoke: login → dashboard stats loaded → navigate to tasks
        → first page has rows → logout → redirected to login.
        """
        # 1. Login
        login = LoginPage(driver, base_url)
        login.open().login_and_wait_for_dashboard("admin", "admin123")

        # 2. Dashboard stats are populated (not "—")
        dashboard = DashboardPage(driver, base_url)
        assert dashboard.total > 0
        assert dashboard.recent_row_count > 0

        # 3. Navigate to tasks
        dashboard.go_to_tasks()
        tasks = TasksPage(driver, base_url)
        assert tasks.get_row_count() == 10

        # 4. Logout
        tasks.click_logout()
        assert "login.html" in tasks.current_url

    # TODO [TICKET-7]: test_create_task_end_to_end
    #   Login → Tasks → New Task → fill form → submit → verify task in list
    #   → open detail page → verify all fields → delete → verify gone
    def test_create_end_to_end(self, tasks_page: TasksPage, task_form: TaskFormPage, task_detail: TaskDetailPage ):
        #Task Data
        title="Newtask"
        description="This is a description"
        priority="CRITICAL"
        status="TODO"
        category="Bug"
        assignee="Tavi"
        due_date="01/05/2025"

        #navigate to tasks
        tasks_page.open()
        assert tasks_page.get_row_count() == 10

        #create new task
        tasks_page.click_new_task()
        task_form.fill(title, description, priority, status, category, assignee, due_date)
        task_form.submit()

        #Verify created task exists and its data is correct
        tasks_page.search(title)
        assert tasks_page.task_title_exists(title)
        task_id = tasks_page.get_task_id(0)
        tasks_page.click_task_title(title)
        details = task_detail.get_details()
        assert details["title"] == title
        assert details["description"] == description
        assert details["priority"] == priority
        assert details["status"] == status
        assert details["category"] == category
        assert details["assignee"] == assignee
        assert details["due_date"] == due_date

        #Delete task and verify its gone
        task_detail.delete_task()
        assert task_id not in tasks_page.get_all_task_ids()



        
        
        #Veryfing the newly created task exists


    # TODO [TICKET-7]: test_search_filter_pagination_journey
    #   Login → Tasks → search "test" → verify results → clear → page 2 →
    #   verify different rows from page 1 → page back → verify page 1 again

    def test_search_filter_pagination_journey(self, tasks_page: TasksPage):
        
        #navigate to tasks
        tasks_page.search("test")
        assert tasks_page.get_row_count() > 0
        tasks_page.clear_filters()
        assert tasks_page.get_row_count() == 10
        first_page_result = tasks_page.get_all_task_ids()
        tasks_page.click_next()
        second_page_result = tasks_page.get_all_task_ids()
        assert set(first_page_result).isdisjoint(second_page_result)
        tasks_page.click_prev()
        first_page_prev_result = tasks_page.get_all_task_ids()
        assert set(first_page_result) == set(first_page_prev_result)



    # TODO [TICKET-7]: test_profile_update_journey
    #   Login → Profile → update name → save → nav bar shows new name →
    #   refresh page → name still updated

    def test_profile_update_journey(self, profile_page: ProfilePage):

        updated_name = "testname"
        profile_page.update_name(updated_name)
        profile_page.save()
        user_name = profile_page.get_user_name()
        assert user_name == updated_name
        profile_page.driver.refresh()
        user_name_after_refresh = profile_page.get_user_name()
        assert user_name_after_refresh == updated_name
        

    # TODO [TICKET-7]: test_task_status_lifecycle
    #   Create task as TODO → edit to IN_PROGRESS → edit to DONE →
    #   verify dashboard "done" count increased by 1

    def test_task_status_lifecycle(self, tasks_page: TasksPage, task_form: TaskFormPage, task_detail: TaskDetailPage, dashboard_page: DashboardPage):
        title="Newtask"
        description="This is a description"
        priority="CRITICAL"
        status="TODO"
        category="Bug"
        assignee="Tavi"
        due_date="01/05/2025"

        next_status = "IN_PROGRESS"
        last_status = "DONE"
        #Snapshot DONE amount
        dashboard_page.open()
        done_tasks_before = dashboard_page.done
        #Create TODO Task
        tasks_page.open()
        tasks_page.click_new_task()
        task_form.fill(title, description, priority, status, category, assignee, due_date)
        task_form.submit()
        #edit to IN_PROGRESS
        tasks_page.search(title)
        tasks_page.click_task_title(title)
        task_detail.edit()
        task_form.fill(title, description, priority, next_status, category, assignee, due_date)
        task_form.submit()
        #edit to DONE
        tasks_page.search(title)
        tasks_page.click_task_title(title)
        task_detail.edit()
        task_form.fill(title, description, priority, last_status, category, assignee, due_date)
        task_form.submit()
        #Snapshot DONE amount
        dashboard_page.open()
        done_tasks_after = dashboard_page.done

        assert done_tasks_after == done_tasks_before + 1

        
