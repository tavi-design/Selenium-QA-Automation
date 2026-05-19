# QA Automation — Task Backlog

> You are a QA Automation Engineer. The webapp is already running. The test
> infrastructure skeleton is in place. Your job is to fill it in. Every ticket
> below is a real task you would get on a team. Complete them in order —
> earlier tickets build the foundations later ones depend on.

---

## HOW TO RUN

```bash
# Terminal 1 — start the webapp
cd webapp && npm install && npm start

# Terminal 2 — run all tests
pytest

# Run only smoke tests
pytest -m smoke

# Run only API tests (no browser needed)
pytest tests/test_api.py

# Run with live output
pytest -s -v
```

Reports are written to `reports/report.html`. Screenshots of failures land in
`reports/screenshots/`.

---

## TICKET-1 — Complete the Page Object Model `[Foundation]`

**Files:** `tests/pages/tasks_page.py`, `tests/pages/task_form_page.py`, `tests/pages/profile_page.py`

The `BasePage`, `LoginPage`, and `DashboardPage` are complete. You need to
finish the rest.

**Acceptance criteria:**

- [*] `TasksPage.filter_by_priority(priority)` — use `selenium.webdriver.support.ui.Select`
- [*] `TasksPage.filter_by_status(status)` — same pattern
- [*] `TasksPage.filter_by_category(category)` — same pattern
- [*] `TasksPage.delete_first_task()` — click Delete on row 0, handle `driver.switch_to.alert`
- [*] `TasksPage.click_task_title(title)` — find the `<a>` in the row that matches, click it
- [*] `TaskFormPage.fill(title, description, priority, status, category, assignee, due_date)` — clear + send_keys for text inputs, `Select` for dropdowns
- [*] `ProfilePage` — add `get_displayed_username()` and `get_displayed_role()` reading the disabled fields

> **Tip:** Never use `driver.find_element` directly in a test — that belongs in
> the page object. Tests should read like plain English.

---

## TICKET-2 — Auth Test Coverage `[Regression]`

**File:** `tests/test_auth.py`

Implement the TODO items already marked in the file, plus:

**Acceptance criteria:**

- [*] Parametrized negative login test covering: wrong password, wrong username, empty username, empty password, SQL injection string
- [*] `test_protected_page_redirects_to_login` — open `/dashboard.html` in a fresh session (use a second driver instance or clear cookies), assert redirect to `/login.html`
- [*] `test_session_persists_after_page_refresh` — login, `driver.refresh()`, assert still on dashboard
- [*] `test_after_logout_protected_pages_redirect` — logout, then navigate to `/tasks.html`, assert redirect
- [*] Add `@pytest.mark.smoke` to the three most critical tests

---

## TICKET-3 — Task CRUD UI Tests `[Regression]`

**File:** `tests/test_tasks_ui.py`

**Acceptance criteria:**

- [*] `test_create_task_appears_in_list` — fill form, submit, search for the title, assert it appears
- [*] `test_create_task_all_fields_saved_correctly` — after create, open detail page, assert every field value matches what was entered
- [*] `test_edit_task_updates_title` — open edit form for task id=1, change title, save, confirm in list
- [*] `test_delete_task_removes_from_list` — delete a task, search for it, assert no-results state
- [*] `test_delete_confirm_cancel_keeps_task` — trigger delete, dismiss the confirm dialog, assert task is still in the table
- [*] All four form validation tests (missing priority, status, category; whitespace-only title)
- [*] Add `@pytest.mark.smoke` to create + delete tests

---

## TICKET-4 — Search & Filter Tests `[Regression]`

**File:** `tests/test_tasks_ui.py` → `TestSearch`

**Acceptance criteria:**

- [*] `test_clear_resets_to_default_count` — search → clear → assert 10 rows back
- [*] `test_filter_by_priority_critical` — filter CRITICAL, assert every visible row contains "CRITICAL" text
- [*] `test_filter_by_status_done` — filter DONE, assert every visible row contains "DONE"
- [*] `test_filter_by_category_testing` — filter Testing category
- [*] `test_combined_filter_high_and_inprogress` — use two filters together, cross-reference result count against `/api/tasks?priority=HIGH&status=IN_PROGRESS`
- [*] `test_search_is_case_insensitive` — search "LOGIN" and "login", assert same results

---

## TICKET-5 — Pagination Tests `[Regression]`

**File:** `tests/test_tasks_ui.py` → `TestPagination`

**Acceptance criteria:**

- [*] `test_last_page_next_button_disabled` — parse `totalPages` from page-info text, navigate there, assert Next disabled
- [*] `test_page_numbers_increment_correctly` — click Next three times, assert page info shows "Page 4" || Only 3 pages are avaliable
- [*] `test_row_count_on_last_page` — 30 seed tasks / 10 per page = 3 pages of 10. Assert page 3 has exactly 10 rows.
- [*] `test_filter_resets_to_page_1` — navigate to page 2, apply a filter, assert page info shows "Page 1"

---

## TICKET-6 — API Test Coverage `[API]`

**File:** `tests/test_api.py`

**Acceptance criteria:**

- [*] Parametrized invalid-login test (4 payloads, all must return 401)
- [*] `test_search_filter_returns_matching_tasks` — all results contain search term
- [*] `test_priority_filter` — all results have the filtered priority
- [*] `test_pagination_page_2_different_from_page_1` — IDs on page 1 ≠ IDs on page 2
- [*] `test_update_task_returns_updated_fields` — PUT with new title, assert response title matches
- [*] `test_update_task_invalid_priority_returns_400`
- [*] `test_stats_values_are_non_negative_integers`
- [*] `test_stats_unauthenticated_returns_401`
- [*] Add `@pytest.mark.api` to every test in this file

---

## TICKET-7 — End-to-End Journeys `[E2E]`

**File:** `tests/test_e2e.py`

One journey is already implemented as a reference. Implement the remaining three:

**Acceptance criteria:**

- [*] `test_create_task_end_to_end` — full create → view → delete journey without touching the API directly
- [*] `test_search_filter_pagination_journey` — multi-step filter + pagination flow
- [*] `test_profile_update_journey` — update name, verify nav bar updates, refresh, verify persists
- [ ] `test_task_status_lifecycle` — move a task through TODO → IN_PROGRESS → DONE, verify dashboard counter

---

## TICKET-8 — Negative & Edge-Case Tests `[Regression]` `[Negative]`

Create a new file: `tests/test_negative.py`

**Acceptance criteria:**

- [ ] XSS attempt in task title — input `<script>alert(1)</script>`, assert it appears as escaped text on the detail page, not executed
- [ ] Very long title (500 chars) — verify it is truncated or rejected cleanly, no 500 error
- [ ] Special characters in search — `& % # @ !` — server must return 200 not 500
- [ ] Create task with past due date — assert it is accepted (or rejected with a clear error, not a crash)
- [ ] Concurrent rapid clicks on Delete — click Delete button twice in quick succession, assert only one request is made (check task count)
- [ ] Add `@pytest.mark.negative` to every test in this file

---

## TICKET-9 — CI/CD Pipeline `[DevOps]`

**File:** `.github/workflows/ci.yml`

The skeleton is in place. Extend it:

**Acceptance criteria:**

- [ ] Smoke tests run on every push to `main` or `develop`
- [ ] Full suite runs only on pull requests (already in skeleton — verify it works)
- [ ] HTML report is uploaded as a GitHub Actions artifact (already in skeleton — verify)
- [ ] Add a job step that fails the workflow if **any** screenshot was captured (i.e. treat any UI failure as a hard failure signal)
- [ ] Add a README badge that shows CI status

---

## TICKET-10 — Test Data & Fixture Hygiene `[Foundation]`

**Files:** `tests/conftest.py`, all test files

**Acceptance criteria:**

- [ ] Create a `fresh_task` pytest fixture in `conftest.py` that POSTs a task via `admin_api`, yields the task dict, and DELETEs it in teardown — no test should rely on a specific seed-data ID
- [ ] Audit TICKET-3 and TICKET-7 tests: replace any hardcoded `id=1` with the `fresh_task` fixture
- [ ] Create a `tests/data/` directory with `users.json` and `tasks.json` containing test data sets
- [ ] Parametrize at least two tests using data loaded from those JSON files

---

## Definition of Done (for all tickets)

- Tests pass locally with `pytest` (no skips, no xfail)
- No `driver.find_element` calls in test files — all selectors live in page objects
- New page object methods have a one-line docstring
- `pytest -m smoke` passes in under 60 seconds
- HTML report generates without errors

---

## Stretch Goals (bonus, no deadline)

- **Allure reporting** — replace pytest-html with Allure; add `@allure.feature` and `@allure.story` decorators
- **Cross-browser** — parametrize the `driver` fixture to run on both Chrome and Firefox (add `geckodriver` to the Dockerfile)
- **Visual regression** — add a screenshot comparison test using `Pillow`
- **Performance assertion** — assert that the tasks page loads in under 2 seconds using `driver.execute_script("return performance.timing...")`
