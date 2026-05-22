import os
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from tests.pages.dashboard_page import DashboardPage
from tests.pages.profile_page import ProfilePage
from tests.pages.tasks_page import TaskDetailPage, TaskFormPage, TasksPage

BASE_URL = os.environ.get("WEBAPP_URL", "http://localhost:3000")
ADMIN_CREDS    = {"username": "admin",    "password": "admin123"}
TESTUSER_CREDS = {"username": "testuser", "password": "user123"}


# ── Browser fixture ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")

    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
    d = webdriver.Chrome(service=service, options=options)
    d.implicitly_wait(0)
    yield d
    d.quit()

# -- FreshTask fixture ---------------------------------

@pytest.fixture
def fresh_task(admin_api, base_url):
    r = admin_api.post(f"{base_url}/api/tasks", json={
        "title" : "Fresh test task",
        "priority" : "MEDIUM",
        "status" : "TODO",
        "category" : "Testing"
    })
    task = r.json()

    yield task

    admin_api.delete(f"{base_url}/api/tasks/{task['id']}")
# ── Screenshot on failure ─────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            os.makedirs("reports/screenshots", exist_ok=True)
            safe = item.nodeid.replace("::", "_").replace("/", "_")
            path = f"reports/screenshots/{safe}.png"
            driver.save_screenshot(path)
            # Attach to pytest-html report
            if hasattr(item, "extras"):
                from pytest_html import extras as html_extras
                item.extras.append(html_extras.image(path))


# ── Shared URL fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


# ── API session fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def api_session():
    """Unauthenticated requests.Session — function-scoped so each test gets a
    clean session with no cookies, even if a previous test called login."""
    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/json"})
        yield s


@pytest.fixture(scope="session")
def admin_api(base_url):
    """requests.Session pre-authenticated as admin."""
    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/json"})
        r = s.post(f"{base_url}/api/auth/login", json=ADMIN_CREDS)
        assert r.status_code == 200, f"Admin login failed: {r.text}"
        yield s


@pytest.fixture(scope="session")
def user_api(base_url):
    """requests.Session pre-authenticated as testuser."""
    with requests.Session() as s:
        s.headers.update({"Content-Type": "application/json"})
        r = s.post(f"{base_url}/api/auth/login", json=TESTUSER_CREDS)
        assert r.status_code == 200, f"Testuser login failed: {r.text}"
        yield s


# ── Logged-in Selenium fixture ────────────────────────────────────────────────

@pytest.fixture
def logged_in_driver(driver, base_url):
    """Browser already authenticated as admin before the test runs."""
    driver.get(f"{base_url}/login.html")
    from tests.pages.login_page import LoginPage
    LoginPage(driver, base_url).login_and_wait_for_dashboard(
        ADMIN_CREDS["username"], ADMIN_CREDS["password"]
    )
    yield driver
    # No logout here — next test can re-use the session



#--Page Fixtures 

@pytest.fixture
def tasks_page(logged_in_driver, base_url):
    page = TasksPage(logged_in_driver, base_url)
    page.open()
    return page


@pytest.fixture
def task_form(logged_in_driver, base_url):
    page = TaskFormPage(logged_in_driver, base_url)
    page.open_new()
    return page

@pytest.fixture
def task_detail(logged_in_driver, base_url):
    page = TaskDetailPage(logged_in_driver, base_url)
    return page

@pytest.fixture
def profile_page(logged_in_driver, base_url):
    page = ProfilePage(logged_in_driver, base_url)
    page.open()
    return page

@pytest.fixture
def dashboard_page(logged_in_driver, base_url):
    page = DashboardPage(logged_in_driver, base_url)
    page.open()
    return page