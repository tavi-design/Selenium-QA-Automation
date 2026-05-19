from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from .base_page import BasePage


class TasksPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    SEARCH_INPUT     = (By.ID, "search-input")
    FILTER_PRIORITY  = (By.ID, "filter-priority")
    FILTER_STATUS    = (By.ID, "filter-status")
    FILTER_CATEGORY  = (By.ID, "filter-category")
    SEARCH_BTN       = (By.ID, "search-btn")
    CLEAR_BTN        = (By.ID, "clear-btn")
    NEW_TASK_BTN     = (By.ID, "new-task-btn")
    TASK_ROWS        = (By.CSS_SELECTOR, "#task-tbody tr[data-task-id]")
    NO_RESULTS       = (By.ID, "no-results")
    PAGE_INFO        = (By.ID, "page-info")
    PREV_BTN         = (By.ID, "prev-btn")
    NEXT_BTN         = (By.ID, "next-btn")
    DELETE_BTN       = (By.CSS_SELECTOR, ".delete-btn")

    def open(self):
        return super().open("/tasks.html")
    
    def _apply_filter(self):
        self.driver.find_element(*self.SEARCH_BTN).click()

    # ── Search / filter ───────────────────────────────────────────────────────

    def search(self, term: str):
        field = self.wait_for_visible(*self.SEARCH_INPUT)
        field.clear()
        field.send_keys(term)
        self.wait_for_clickable(*self.SEARCH_BTN).click()
        return self

    def filter_by_priority(self, priority: str):
        select = Select(self.driver.find_element(*self.FILTER_PRIORITY))
        select.select_by_visible_text(priority)
        self._apply_filter()

    def filter_by_status(self, status: str):
        select = Select(self.driver.find_element(*self.FILTER_STATUS))
        select.select_by_visible_text(status)
        self._apply_filter()

    def filter_by_category(self, category: str):
        select = Select(self.driver.find_element(*self.FILTER_CATEGORY))
        select.select_by_visible_text(category)
        self._apply_filter()

    def clear_filters(self):
        before = self.driver.find_element(*self.SEARCH_INPUT).get_attribute("value")
        self.wait_for_clickable(*self.CLEAR_BTN).click()
        self._wait.until(lambda d: d.find_element(*self.SEARCH_INPUT).get_attribute("value") != before)
        return self

    # ── Table ─────────────────────────────────────────────────────────────────

    def get_task_rows(self):
        self._wait.until(lambda d: d.find_elements(*self.TASK_ROWS) or
                         d.find_elements(*self.NO_RESULTS))
        return self.driver.find_elements(*self.TASK_ROWS)

    def get_row_count(self) -> int:
        return len(self.get_task_rows())

    def get_page_info_text(self) -> str:
        return self.wait_for_element(*self.PAGE_INFO).text

    def is_no_results_visible(self) -> bool:
        # NO_RESULTS is injected by JS after fetch — wait for it to appear
        try:
            self._wait.until(EC.visibility_of_element_located(self.NO_RESULTS))
            return True
        except Exception:
            return False
        
    def task_title_exists(self, title) -> bool:
        rows = self.get_task_rows()
        if not rows:
            return False
        for row in rows:
            title_cell = row.find_element(By.XPATH, ".//td[@class='title-cell']/a")
            row_title = title_cell.text
            if row_title == title:
                return True
        return False
    
    def get_task_id(self, index: int) -> str:
        rows = self.get_task_rows()
        if not rows:
            raise RuntimeError("No rows found to fetch ID")
        return rows[index].get_attribute("data-task-id")
    
    def get_all_task_ids(self) -> list[str]:
        rows = self.get_task_rows()
        ids = []
        if not rows:
            raise RuntimeError("No rows found to fetch ID")
        for row in rows:
            ids.append(row.get_attribute("data-task-id"))
        return ids
    
    def get_all_tasks_priorities(self) -> list[str]:
        rows = self.get_task_rows()
        priorities = []
        if not rows:
            raise RuntimeError("No rows found to fetch priorities")
        for row in rows: 
            priorities.append(row.find_element(By.XPATH, ".//td[3]/span").text)
        return priorities
    
    def get_all_tasks_statuses(self) -> list[str]:
        rows = self.get_task_rows()
        statuses = []
        if not rows:
            raise RuntimeError("No rows found to fetch statuses")
        for row in rows: 
            statuses.append(row.find_element(By.XPATH, ".//td[4]/span").text)
        return statuses
    
    def get_all_tasks_categories(self) -> list[str]:
        rows = self.get_task_rows()
        categories = []
        if not rows:
            raise RuntimeError("No rows found to fetch categories")
        for row in rows:
            categories.append(row.find_element(By.XPATH, ".//td[5]").text)
        return categories

    # ── Pagination ────────────────────────────────────────────────────────────

    def click_next(self):
        before = self.driver.find_element(*self.PAGE_INFO).text
        self.wait_for_clickable(*self.NEXT_BTN).click()
        self._wait.until(lambda d: d.find_element(*self.PAGE_INFO).text != before)
        return self

    def click_prev(self):
        before = self.driver.find_element(*self.PAGE_INFO).text
        self.wait_for_clickable(*self.PREV_BTN).click()
        self._wait.until(lambda d: d.find_element(*self.PAGE_INFO).text != before)
        return self

    def is_prev_disabled(self) -> bool:
        return self.driver.find_element(*self.PREV_BTN).get_attribute("disabled") is not None

    def is_next_disabled(self) -> bool:
        return self.driver.find_element(*self.NEXT_BTN).get_attribute("disabled") is not None
    
    def go_to_last_page(self):
        while not self.is_next_disabled():
            self.click_next()

    def get_current_page(self) -> str:
        page_info = self.get_page_info_text()
        page_info_split = page_info.split(" ")
        page_index = next((i for i, v in enumerate(page_info_split) if "Page" in v), -1)
        
        return page_info_split[page_index+1]
        


    # ── Actions ───────────────────────────────────────────────────────────────

    def click_new_task(self):
        self.wait_for_clickable(*self.NEW_TASK_BTN).click()
        self.wait_for_url_contains("task-form.html")

    def delete_first_task(self):
        rows = self.get_task_rows()
        if not rows:
            raise RuntimeError("No task rows found to delete")
        delete_btn = rows[0].find_element(*self.DELETE_BTN)
        delete_btn.click()
        # Alert handling
        self.driver.switch_to.alert.accept()
    
    def cancel_delete_first_task(self):
        rows = self.get_task_rows()
        if not rows: 
            raise RuntimeError("No task rows found to delete")
        delete_btn = rows[0].find_element(*self.DELETE_BTN)
        delete_btn.click()
        self.driver.switch_to.alert.dismiss()


    def click_task_title(self, title: str):
        locator = (By.XPATH, f"//td[@class='title-cell']/a[text()='{title}']")
        self.wait_for_clickable(*locator).click()



class TaskFormPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    TITLE_INPUT       = (By.ID, "title")
    DESCRIPTION_INPUT = (By.ID, "description")
    PRIORITY_SELECT   = (By.ID, "priority")
    STATUS_SELECT     = (By.ID, "status")
    CATEGORY_SELECT   = (By.ID, "category")
    ASSIGNEE_INPUT    = (By.ID, "assignee")
    DUE_DATE_INPUT    = (By.ID, "dueDate")
    SUBMIT_BTN        = (By.ID, "submit-btn")
    TITLE_ERROR       = (By.ID, "title-error")
    PRIORITY_ERROR    = (By.ID, "priority-error")
    STATUS_ERROR      = (By.ID, "status-error")
    CATEGORY_ERROR    = (By.ID, "category-error")
    FORM_ERROR        = (By.ID, "form-error")
    FORM_SUCCESS      = (By.ID, "form-success")

    def open_new(self):
        return super().open("/task-form.html")

    def open_edit(self, task_id: int):
        return super().open(f"/task-form.html?id={task_id}")

    def fill(self, title="", description="", priority="", status="", category="", assignee="", due_date=""):
        title_selector = self.driver.find_element(*self.TITLE_INPUT)
        description_selector = self.driver.find_element(*self.DESCRIPTION_INPUT)
        priority_select = Select(self.driver.find_element(*self.PRIORITY_SELECT))
        status_select = Select(self.driver.find_element(*self.STATUS_SELECT))
        category_select = Select(self.driver.find_element(*self.CATEGORY_SELECT))
        assignee_selector = self.driver.find_element(*self.ASSIGNEE_INPUT)
        date_selector = self.driver.find_element(*self.DUE_DATE_INPUT)

        title_selector.clear()
        description_selector.clear()
        assignee_selector.clear()
        date_selector.clear()

        if title:
            title_selector.send_keys(title)
        if description:
            description_selector.send_keys(description)
        if priority:
            priority_select.select_by_visible_text(priority)
        if status:
            status_select.select_by_visible_text(status)
        if category:
            category_select.select_by_visible_text(category)
        if assignee:
            assignee_selector.send_keys(assignee)
        if due_date:
            date_selector.send_keys(due_date)

    def submit(self):
        self.wait_for_clickable(*self.SUBMIT_BTN).click()
        return self

    @property
    def title_error(self) -> str:
        return self.driver.find_element(*self.TITLE_ERROR).text
    
    @property
    def priority_empty_error(self) -> str:
        return self.driver.find_element(*self.PRIORITY_ERROR).text
    
    @property
    def status_empty_error(self) -> str:
        return self.driver.find_element(*self.STATUS_ERROR).text
    
    @property 
    def category_empty_error(self) -> str: 
        return self.driver.find_element(*self.CATEGORY_ERROR).text
    
    @property
    def form_success(self) -> str:
        return self.wait_for_element(*self.FORM_SUCCESS).text
    

class TaskDetailPage(BasePage):
    #LOCATORS
    TASK_TITLE = (By.ID, "task-title")
    EDIT_BTN = (By.ID, "edit-btn")
    DELETE_BTN = (By.ID, "delete-btn")

    def edit(self):
        self.driver.find_element(*self.EDIT_BTN).click()
        self.wait_for_url_contains("task-form.html")

    def delete_task(self):
        self.driver.find_element(*self.DELETE_BTN).click()
        self.driver.switch_to.alert.accept()
        self.wait_for_url_contains("tasks.html")


    def get_details(self) -> dict:
        rows = self.driver.find_elements(By.XPATH, "//tbody[@id='detail-body']/tr")
        result = {}


        def find_value(row) -> str:
            spans = row.find_elements(By.XPATH, ".//td[2]/span")
            if spans:
                return spans[0].text
            return row.find_element(By.XPATH, ".//td[2]").text

        result["title"] = self.driver.find_element(*self.TASK_TITLE).text

        for row in rows:
            data_name = row.find_element(By.XPATH, ".//td[1]").text
            value = find_value(row)
            match data_name:
                case "Priority":
                    result["priority"] = value
                case "Status":
                    result["status"] = value
                case "Category":
                    result["category"] = value
                case "Assignee":
                    result["assignee"] = value
                case "Due Date":
                    if value != "—":
                        result["due_date"] = datetime.strptime(value, "%Y-%m-%d").strftime("%m/%d/%Y")
                    else: 
                        result["due_date"] = None
                case "Description":
                    result["description"] = value
                case _:
                    print(f"Row {data_name} value {value} is not tested for but is present in the details")
        return result        
