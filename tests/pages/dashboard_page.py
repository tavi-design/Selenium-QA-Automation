from selenium.webdriver.common.by import By
from .base_page import BasePage


class DashboardPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    STAT_TOTAL      = (By.ID, "stat-total")
    STAT_TODO       = (By.ID, "stat-todo")
    STAT_INPROGRESS = (By.ID, "stat-inprogress")
    STAT_DONE       = (By.ID, "stat-done")
    STAT_BLOCKED    = (By.ID, "stat-blocked")
    STAT_OVERDUE    = (By.ID, "stat-overdue")
    STAT_CRITICAL   = (By.ID, "stat-critical")
    RECENT_ROWS     = (By.CSS_SELECTOR, "#recent-tbody tr")
    # VIEW_ALL_BTN    = (By.)

    def open(self):
        return super().open("/dashboard.html")

    # ── Getters ───────────────────────────────────────────────────────────────

    def get_stat(self, stat_id: str) -> int:
        self._wait.until(lambda d: d.find_element(By.ID, stat_id).text.isdigit())
        text = self.wait_for_element(By.ID, stat_id).text
        return int(text)

    @property
    def total(self) -> int:
        return self.get_stat("stat-total")

    @property
    def todo(self) -> int:
        return self.get_stat("stat-todo")

    @property
    def done(self) -> int:
        return self.get_stat("stat-done")

    @property
    def overdue(self) -> int:
        return self.get_stat("stat-overdue")

    @property
    def recent_row_count(self) -> int:
        self.wait_for_element(*self.RECENT_ROWS)
        rows = self.driver.find_elements(*self.RECENT_ROWS)
        return len(rows)

    # TODO: Add method to click "View all" link
    def view_all(self):
        self.driver.find_element()
    # TODO: Add method to click a task title in the recent list
