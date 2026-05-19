from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver



class BasePage:
    """Shared helpers inherited by every page object."""

    def __init__(self, driver, base_url: str):
        self.driver: WebDriver = driver
        self.base_url = base_url
        self._wait = WebDriverWait(driver, 10)

    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self, path: str = ""):
        self.driver.get(f"{self.base_url}{path}")
        return self

    @property
    def title(self) -> str:
        return self.driver.title

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ── Wait helpers ──────────────────────────────────────────────────────────

    def wait_for_element(self, by: str, value: str):
        return self._wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_visible(self, by: str, value: str):
        return self._wait.until(EC.visibility_of_element_located((by, value)))

    def wait_for_clickable(self, by: str, value: str):
        return self._wait.until(EC.element_to_be_clickable((by, value)))

    def wait_for_url_contains(self, fragment: str):
        self._wait.until(EC.url_contains(fragment))

    def wait_for_text_in_element(self, by: str, value: str, text: str):
        self._wait.until(EC.text_to_be_present_in_element((by, value), text))

    # ── Nav bar actions ───────────────────────────────────────────────────────

    def click_logout(self):
        self.wait_for_clickable(By.ID, "logout-btn").click()
        self.wait_for_url_contains("login.html")

    def go_to_tasks(self):
        self.driver.find_element(By.LINK_TEXT, "Tasks").click()
        self.wait_for_url_contains("tasks.html")

    def go_to_dashboard(self):
        self.driver.find_element(By.LINK_TEXT, "Dashboard").click()
        self.wait_for_url_contains("dashboard.html")

    def go_to_profile(self):
        self.driver.find_element(By.LINK_TEXT, "Profile").click()
        self.wait_for_url_contains("profile.html")

    # -- Nav bar info ----
    
    def get_user_name(self) -> str:
        self._wait.until(EC.visibility_of_element_located((By.ID, "nav-user")))
        user_name = self.driver.find_element(By.ID, "nav-user").text
        return user_name
