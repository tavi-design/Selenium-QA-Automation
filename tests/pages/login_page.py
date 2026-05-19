from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON   = (By.ID, "login-btn")
    ERROR_MESSAGE  = (By.ID, "login-error")

    def open(self):
        return super().open("/login.html")

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_username(self, username: str):
        field = self.wait_for_visible(*self.USERNAME_INPUT)
        field.clear()
        field.send_keys(username)
        return self

    def enter_password(self, password: str):
        field = self.wait_for_visible(*self.PASSWORD_INPUT)
        field.clear()
        field.send_keys(password)
        return self

    def click_login(self):
        self.wait_for_clickable(*self.LOGIN_BUTTON).click()
        return self

    def login(self, username: str, password: str):
        """Full login flow — returns self for chaining."""
        return self.enter_username(username).enter_password(password).click_login()

    def login_and_wait_for_dashboard(self, username: str, password: str):
        self.login(username, password)
        self.wait_for_url_contains("dashboard.html")

    # ── Assertions ────────────────────────────────────────────────────────────

    @property
    def error_message(self) -> str:
        return self.wait_for_element(*self.ERROR_MESSAGE).text

    def is_error_visible(self) -> bool:
        # Wait up to 5s for the async fetch to complete and populate the element
        try:
            self._wait.until(
                lambda d: d.find_element(*self.ERROR_MESSAGE).text.strip()
            )
            return True
        except Exception:
            return False
