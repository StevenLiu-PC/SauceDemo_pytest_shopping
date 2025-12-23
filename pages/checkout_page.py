from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



class CheckoutPage:
    """Checkout Step 1 / Step 2 Page Object"""

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BTN = (By.ID, "continue")
    
    TITLE = (By.CLASS_NAME, "title")
    FINISH_BTN = (By.ID, "finish")
    STEP_TWO_URL_KEYWORD = "checkout-step-two"
    CANCEL_BTN = (By.ID, "cancel")

    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")
    ERROR_CONTAINER = (By.CLASS_NAME, "error-message-container")


    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def fill_step_one(self, first_name: str, last_name: str, postal_code: str):
        """填寫 Step 1 的基本資料並按 Continue"""
        # 等 Step 1 表單出現
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))

        first_name_input = self.driver.find_element(*self.FIRST_NAME)
        first_name_input.clear()
        first_name_input.send_keys(first_name)

        last_name_input = self.driver.find_element(*self.LAST_NAME)
        last_name_input.clear()
        last_name_input.send_keys(last_name)

        postal_code_input = self.driver.find_element(*self.POSTAL_CODE)
        postal_code_input.clear()
        postal_code_input.send_keys(postal_code)

        self.driver.find_element(*self.CONTINUE_BTN).click()

        #  只做一個到站確認：Step 2 的 Finish 出現
        self.wait.until(EC.visibility_of_element_located(self.FINISH_BTN))

    def submit_step_one(self, first_name: str, last_name: str, postal_code: str):
        """Step1 送出（不保證成功、不等 Step2；給錯誤測試用）"""
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))

        first_name_input = self.driver.find_element(*self.FIRST_NAME)
        first_name_input.clear()
        first_name_input.send_keys(first_name)

        last_name_input = self.driver.find_element(*self.LAST_NAME)
        last_name_input.clear()
        last_name_input.send_keys(last_name)

        postal_code_input = self.driver.find_element(*self.POSTAL_CODE)
        postal_code_input.clear()
        postal_code_input.send_keys(postal_code)

        self.driver.find_element(*self.CONTINUE_BTN).click()
    
    def is_on_step_two(self) -> bool:
        """確認是否已經進入 Step 2 有看到 title """
        try:
            self.wait.until(EC.visibility_of_element_located(self.FINISH_BTN))
            return True
        except TimeoutException:
        # 這行可幫 debug，看到現在到底在哪一頁
            print("DEBUG: still not on step two, current url =", self.driver.current_url)
            return False
    def click_finish(self):
        """Step2 按 Finish → 完成頁"""
        self.wait.until(EC.element_to_be_clickable(self.FINISH_BTN)).click()

    def click_cancel_on_step_two(self):
        """Step2 按 Cancel → 回 inventory"""
        self.wait.until(EC.element_to_be_clickable(self.CANCEL_BTN)).click()

    def get_error_message(self) -> str:
        """拿錯誤訊息（沒有就回空字串）"""
        elements = self.driver.find_elements(*self.ERROR_MESSAGE)
        return elements[0].text.strip() if elements else ""