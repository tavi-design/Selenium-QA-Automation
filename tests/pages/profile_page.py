from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProfilePage(BasePage):
    NAME_INPUT      = (By.ID, "name")
    EMAIL_INPUT     = (By.ID, "email")
    SAVE_BTN        = (By.ID, "save-profile-btn")
    SUCCESS_MSG     = (By.ID, "profile-success")
    NAME_ERROR      = (By.ID, "name-error")
    EMAIL_ERROR     = (By.ID, "email-error")

    def open(self):
        return super().open("/profile.html")

    def update_name(self, name: str):
        field = self.wait_for_visible(*self.NAME_INPUT)
        field.clear()
        field.send_keys(name)
        return self

    def update_email(self, email: str):
        field = self.wait_for_visible(*self.EMAIL_INPUT)
        field.clear()
        field.send_keys(email)
        return self

    def save(self):
        self.wait_for_clickable(*self.SAVE_BTN).click()
        self.wait_for_element(*self.SUCCESS_MSG)
        return self

    @property
    def success_message(self) -> str:
        return self.wait_for_element(*self.SUCCESS_MSG).text

    def get_displayed_username(self) -> str:
        username = self.driver.find_element(By.XPATH, "//input[@id='username-display']").get_attribute("value")
        return username
    def get_displayed_role(self) -> str:
        role = self.driver.find_element(By.XPATH, "//input[@id='role-display']").get_attribute("value")
        return role