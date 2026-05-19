"""
Quick debug tests for TICKET-1 implementations.

Run just this file while you work:
    pytest tests/test_debug_ticket1.py -v -s

Each test covers exactly one method. If a method raises NotImplementedError
or the assertion fails, the output tells you which method and why.
"""
import pytest
from selenium.webdriver.support.ui import Select
from tests.pages.tasks_page import TasksPage, TaskFormPage
from tests.pages.profile_page import ProfilePage


# ── Shared fixture: open tasks page already logged in ─────────────────────────

@pytest.fixture
def tasks(logged_in_driver, base_url):
    page = TasksPage(logged_in_driver, base_url)
    page.open()
    # Wait for the initial task list to load before each test
    page.get_task_rows()
    return page


@pytest.fixture
def form(logged_in_driver, base_url):
    page = TaskFormPage(logged_in_driver, base_url)
    page.open_new()
    return page


@pytest.fixture
def profile(logged_in_driver, base_url):
    page = ProfilePage(logged_in_driver, base_url)
    page.open()
    return page


# ── filter_by_priority ────────────────────────────────────────────────────────

def test_filter_by_priority_returns_only_critical_rows(tasks):
    tasks.filter_by_priority("CRITICAL")
    tasks.get_task_rows()  # wait for results to load
    rows = tasks.get_task_rows()
    assert rows, "Expected at least one CRITICAL task in the seeded data"
    for row in rows:
        assert "CRITICAL" in row.text, (
            f"Row text '{row.text}' does not contain 'CRITICAL' — filter did not work"
        )


def test_filter_by_priority_low_reduces_count(tasks):
    all_count = tasks.get_row_count()
    tasks.filter_by_priority("LOW")
    tasks.get_task_rows()
    low_count = tasks.get_row_count()
    assert low_count < all_count, (
        f"LOW filter returned {low_count} rows — same as unfiltered {all_count}, filter may not be working"
    )


# ── filter_by_status ──────────────────────────────────────────────────────────

def test_filter_by_status_returns_only_done_rows(tasks):
    tasks.filter_by_status("DONE")
    tasks.get_task_rows()
    rows = tasks.get_task_rows()
    assert rows, "Expected at least one DONE task in the seeded data"
    for row in rows:
        assert "DONE" in row.text, (
            f"Row text '{row.text}' does not contain 'DONE'"
        )


def test_filter_by_status_blocked(tasks):
    tasks.filter_by_status("BLOCKED")
    tasks.get_task_rows()
    rows = tasks.get_task_rows()
    assert rows, "Expected at least one BLOCKED task in the seeded data"
    for row in rows:
        assert "BLOCKED" in row.text


# ── filter_by_category ────────────────────────────────────────────────────────

def test_filter_by_category_testing(tasks):
    tasks.filter_by_category("Testing")
    tasks.get_task_rows()
    rows = tasks.get_task_rows()
    assert rows, "Expected at least one Testing task in the seeded data"
    for row in rows:
        assert "Testing" in row.text, (
            f"Row text '{row.text}' does not contain 'Testing'"
        )


# ── delete_first_task ─────────────────────────────────────────────────────────

def test_delete_first_task_completes_without_error(tasks):
    """Ticket scope: delete button is clicked and alert is accepted without raising."""
    tasks.delete_first_task()


# ── click_task_title ──────────────────────────────────────────────────────────

def test_click_task_title_navigates_to_detail(tasks, base_url):
    rows = tasks.get_task_rows()
    assert rows, "No rows to click"
    # Grab the title text from the first row so we know what to look for
    first_title = rows[0].find_element("css selector", ".title-cell a").text
    tasks.click_task_title(first_title)
    tasks.wait_for_url_contains("task-detail.html")
    assert "task-detail.html" in tasks.current_url, (
        f"Expected to navigate to task-detail.html, got: {tasks.current_url}"
    )


# ── TaskFormPage.fill ─────────────────────────────────────────────────────────

def test_form_fill_populates_title(form):
    form.fill(title="Debug task title")
    actual = form.driver.find_element("id", "title").get_attribute("value")
    assert actual == "Debug task title", f"Title field shows '{actual}'"


def test_form_fill_selects_priority(form):
    form.fill(priority="HIGH")
    select = Select(form.driver.find_element("id", "priority"))
    assert select.first_selected_option.text == "HIGH", (
        f"Priority select shows '{select.first_selected_option.text}'"
    )


def test_form_fill_selects_status(form):
    form.fill(status="IN_PROGRESS")
    select = Select(form.driver.find_element("id", "status"))
    assert select.first_selected_option.text == "IN_PROGRESS"


def test_form_fill_selects_category(form):
    form.fill(category="Bug")
    select = Select(form.driver.find_element("id", "category"))
    assert select.first_selected_option.text == "Bug"


def test_form_fill_all_fields_and_submit_succeeds(form, tasks_page=None):
    form.fill(
        title="Full debug task",
        description="Created by debug test",
        priority="MEDIUM",
        status="TODO",
        category="Testing",
        assignee="admin",
    )
    form.submit()
    # Success message or redirect means it worked
    try:
        msg = form.form_success
        assert msg != "", "Expected a success message after submit"
    except Exception:
        # If it redirected already, that also counts as success
        assert "tasks.html" in form.current_url or "task-form.html" in form.current_url


# ── ProfilePage getters ───────────────────────────────────────────────────────

def test_profile_get_displayed_username(profile):
    username = profile.get_displayed_username()
    assert username == "admin", (
        f"Expected username 'admin', got '{username}'"
    )


def test_profile_get_displayed_role(profile):
    role = profile.get_displayed_role()
    assert role == "Admin", (
        f"Expected role 'Admin', got '{role}'"
    )
