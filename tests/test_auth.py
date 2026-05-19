"""
Authentication test suite.

FULLY IMPLEMENTED — use this as the reference for style and POM usage.
Your job (see TASKS.md): add the parametrized negative-login cases and the
session-persistence test.
"""
import pytest
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage
from tests.pages.base_page import BasePage


@pytest.fixture
def login_page(driver, base_url):
    page = LoginPage(driver, base_url)
    page.open()
    return page


# ── Positive ──────────────────────────────────────────────────────────────────

class TestLoginSuccess:
    @pytest.mark.smoke
    def test_admin_login_reaches_dashboard(self, login_page):
        login_page.login_and_wait_for_dashboard("admin", "admin123")
        assert "dashboard.html" in login_page.current_url

    def test_dashboard_title_after_login(self, login_page):
        login_page.login_and_wait_for_dashboard("admin", "admin123")
        assert login_page.title == "Dashboard – Task Manager"

    def test_nav_shows_username_after_login(self, login_page, driver, base_url):
        login_page.login_and_wait_for_dashboard("admin", "admin123")
        dashboard = DashboardPage(driver, base_url)
        assert "Admin User" in driver.find_element("id", "nav-user").text


# ── Negative ──────────────────────────────────────────────────────────────────

class TestLoginFailure:
    def test_wrong_password_shows_error(self, login_page):
        login_page.login("admin", "wrongpassword")
        assert login_page.is_error_visible()
        assert "Invalid" in login_page.error_message

    def test_wrong_username_shows_error(self, login_page):
        login_page.login("nobody", "admin123")
        assert login_page.is_error_visible()

    def test_empty_credentials_shows_error(self, login_page):
        login_page.click_login()
        assert login_page.is_error_visible()
    @pytest.mark.smoke
    def test_wrong_credentials_stay_on_login_page(self, login_page):
        login_page.login("admin", "bad")
        assert "login.html" in login_page.current_url

    @pytest.mark.parametrize("username,password", [
        ("", "admin123"),
         ("admin", ""),
         ("",""),
         ("wrongusername", "admin123"),
         ("admin", "wrongpassword"),
         ("' OR 1=1 --", "x")
    ])
    def test_invalid_login(self, login_page, username, password):
        login_page.login(username, password)
        assert login_page.is_error_visible()

    def test_protected_page_redirects_to_login(self, driver, base_url):
        driver.delete_all_cookies()
        dashboard = DashboardPage(driver, base_url)
        dashboard.open()
        assert "login.html" in dashboard.current_url

    def test_session_persists_after_page_refresh(self,driver, login_page, base_url):
        #dashboard = DashboardPage(driver, base_url)
        #dashboard.open()
        login_page.login_and_wait_for_dashboard("admin", "admin123")
        driver.refresh()
        assert "dashboard.html" in login_page.current_url
    # TODO [TICKET-2]: test_session_persists_after_page_refresh
    #   — login, refresh, assert still on dashboard (not redirected to login)


# ── Logout ────────────────────────────────────────────────────────────────────

class TestLogout:
    def test_logout_redirects_to_login(self, logged_in_driver, base_url):
        page = BasePage(logged_in_driver, base_url)
        page.click_logout()
        assert "login.html" in page.current_url

    @pytest.mark.smoke
    def test_after_logout_protected_pages_redirect(self, logged_in_driver, base_url):
        dashboard = DashboardPage(logged_in_driver, base_url)
        dashboard.click_logout()
        dashboard.open()
        assert "login.html" in dashboard.current_url

    # TODO [TICKET-2]: test_after_logout_protected_pages_redirect
    #   — after logout, navigate to /dashboard.html, assert redirect to /login.html
