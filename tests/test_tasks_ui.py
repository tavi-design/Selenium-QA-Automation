"""
Task management UI test suite.

PARTIALLY IMPLEMENTED — the working examples show the pattern.
Complete the TODOs marked with TICKET numbers (see TASKS.md).
"""
import pytest
from tests.pages.tasks_page import TaskDetailPage, TasksPage, TaskFormPage
from tests.pages.dashboard_page import DashboardPage


# ── Page load ─────────────────────────────────────────────────────────────────

class TestTasksPageLoad:
    def test_page_title(self, tasks_page):
        assert tasks_page.title == "Tasks – Task Manager"

    def test_default_shows_ten_rows(self, tasks_page):
        assert tasks_page.get_row_count() == 10

    def test_page_info_shows_page_1(self, tasks_page):
        assert "Page 1" in tasks_page.get_page_info_text()

    def test_prev_button_disabled_on_first_page(self, tasks_page):
        assert tasks_page.is_prev_disabled()


# ── Search ────────────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_filters_results(self, tasks_page: TasksPage):
        tasks_page.search("login")
        rows = tasks_page.get_task_rows()
        assert len(rows) >= 1

    def test_search_no_match_shows_empty_state(self, tasks_page: TasksPage):
        tasks_page.search("zzznoresultszzz")
        assert tasks_page.is_no_results_visible()


    def test_clear_resets_search(self, tasks_page: TasksPage):
        original_rows = tasks_page.get_all_task_ids()
        tasks_page.search("login")
        tasks_page.clear_filters()
        cleared_rows = tasks_page.get_all_task_ids()
        assert original_rows == cleared_rows


    def test_filter_by_priority_critical(self, tasks_page: TasksPage):
        tasks_page.filter_by_priority("CRITICAL")
        assert all(priority == "CRITICAL" for priority in tasks_page.get_all_tasks_priorities())
        
        

    def test_filter_by_status_done(self, tasks_page: TasksPage):
        tasks_page.filter_by_status("DONE")
        assert all(status == "DONE" for status in tasks_page.get_all_tasks_statuses())


    def test_filter_by_category_testing(self, tasks_page: TasksPage):
        tasks_page.filter_by_category("Testing")
        assert all(category == "Testing" for category in tasks_page.get_all_tasks_categories())

    def test_combined_filter_priority_and_status(self, tasks_page: TasksPage, admin_api, base_url):
        tasks_page.filter_by_status("IN_PROGRESS")
        tasks_page.filter_by_priority("HIGH")
        api_response = admin_api.get(f"{base_url}/api/tasks?priority=HIGH&status=IN_PROGRESS")
        api_count = api_response.json()["total"]
        rows_len = len(tasks_page.get_task_rows())
        assert rows_len  == api_count

    def test_search_is_case_insensitive(self, tasks_page: TasksPage):
        search_query = "fix"
        tasks_page.search(search_query)
        lower_case_result = tasks_page.get_all_task_ids()
        tasks_page.search(search_query.upper())
        upper_case_result = tasks_page.get_all_task_ids()
        assert set(upper_case_result) == set(lower_case_result)



# ── Pagination ────────────────────────────────────────────────────────────────

class TestPagination:
    def test_next_loads_page_2(self, tasks_page):
        tasks_page.click_next()
        assert "Page 2" in tasks_page.get_page_info_text()

    def test_prev_returns_to_page_1(self, tasks_page):
        tasks_page.click_next()
        tasks_page.click_prev()
        assert "Page 1" in tasks_page.get_page_info_text()

    def test_last_page_next_button_disabled(self, tasks_page: TasksPage):
        tasks_page.go_to_last_page()
        assert tasks_page.is_next_disabled()


    def test_row_count_on_last_page(self, tasks_page: TasksPage):
        tasks_page.go_to_last_page()
        assert tasks_page.get_row_count() == 10

    def test_page_numbers_increment_correctly(self, tasks_page: TasksPage):
        tasks_page.click_next()
        tasks_page.click_next()
        assert tasks_page.get_current_page() == "3"

    def test_filter_resets_to_page_1(self, tasks_page: TasksPage):
        tasks_page.click_next()
        tasks_page.filter_by_category("Bug")
        assert tasks_page.get_current_page() == "1"



# ── Create / Edit / Delete ────────────────────────────────────────────────────

class TestTaskCRUD:

    @pytest.mark.smoke
    def test_create_task_appears_in_list(self, tasks_page, task_form):
        title = "create task test"
        description = "this is a test"
        priority = "CRITICAL"
        status = "TODO"
        category = "Feature"
        assignee = "Tester"
        due_date = "01/05/2025"
        task_form.fill(title, description, priority, status, category, assignee, due_date)
        task_form.submit()
        tasks_page.open()
        tasks_page.search(title)
        assert tasks_page.task_title_exists(title) 


    def test_create_task_all_fields_saved_correctly(self, tasks_page, task_form, task_detail):
        title = "create task test saved"
        description = "this is a test"
        priority = "CRITICAL"
        status = "TODO"
        category = "Feature"
        assignee = "Tester"
        due_date = "01/05/2025"
        task_form.fill(title, description, priority, status, category, assignee, due_date)
        task_form.submit()
        tasks_page.open()
        tasks_page.search(title)
        tasks_page.click_task_title(title)
        details = task_detail.get_details()
        assert details["title"] == title
        assert details["description"] == description
        assert details["priority"] == priority
        assert details["status"] == status
        assert details["category"] == category
        assert details["assignee"] == assignee
        assert details["due_date"] == due_date



    def test_edit_task_updates_title(self, tasks_page: TasksPage, task_form: TaskFormPage , task_detail: TaskDetailPage):
        title = "create task test saved"
        edited_title = "This title has been edited"
        description = "this is a test"
        priority = "CRITICAL"
        status = "TODO"
        category = "Feature"
        assignee = "Tester"
        due_date = "01/05/2025"
        task_form.fill(title, description, priority, status, category, assignee, due_date)
        task_form.submit()
        tasks_page.open()
        tasks_page.search(title)
        tasks_page.click_task_title(title)
        task_detail.edit()
        task_form.fill(edited_title, description, priority, status, category, assignee, due_date)
        task_form.submit()
        tasks_page.open()
        tasks_page.search(edited_title)
        tasks_page.click_task_title(edited_title)
        details = task_detail.get_details()
        assert details["title"] == edited_title


    @pytest.mark.smoke
    def test_delete_task_removes_from_list(self, tasks_page: TasksPage):
        deleted_task = tasks_page.get_task_id(0)
        tasks_page.delete_first_task()
        assert deleted_task not in tasks_page.get_all_task_ids()



    def test_delete_confirm_cancel_keeps_task(self, tasks_page: TasksPage):
        first_task_id = tasks_page.get_task_id(0)
        tasks_page.cancel_delete_first_task()
        assert tasks_page.get_task_id(0) == first_task_id
    



# ── Form validation ───────────────────────────────────────────────────────────

class TestTaskFormValidation:
    def test_submit_empty_form_shows_title_error(self, task_form: TaskFormPage):
        task_form.fill(priority="LOW", status="TODO", category="Bug")
        task_form.submit()
        assert task_form.title_error != ""

    # TODO [TICKET-3]: test_missing_priority_shows_error
    def test_missing_priority_shows_error(self, task_form: TaskFormPage):
        task_form.fill(title="test title", status="TODO", category="Bug")
        task_form.submit()
        assert task_form.priority_empty_error != ""

    
    # TODO [TICKET-3]: test_missing_status_shows_error
    def test_missing_status_shows_error(self, task_form: TaskFormPage):
        task_form.fill(title="test title", priority="LOW", category="Bug")
        task_form.submit()
        assert task_form.status_empty_error != ""
    # TODO [TICKET-3]: test_missing_category_shows_error
    def test_missing_category_shows_error(self, task_form: TaskFormPage):
        task_form.fill(title="test title", priority="LOW", status="TODO")
        task_form.submit()
        assert task_form.category_empty_error != ""

    # TODO [TICKET-3]: test_title_only_whitespace_shows_error
    #   — send_keys("   ") for title, submit, assert error
    def test_title_only_whitespace_shows_error(self, task_form: TaskFormPage): 
        task_form.fill(title= "      ", priority="LOW", status="TODO", category="Bug")
        task_form.submit()
        assert task_form.title_error != ""
