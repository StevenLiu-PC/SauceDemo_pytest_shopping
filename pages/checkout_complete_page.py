from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CheckoutCompletePage:
    """Checkout Complete Page"""

    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")  # Thank you for your order!
    BACK_HOME_BTN = (By.ID, "back-to-products")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_for_loaded(self):
        """ 確認這頁載入完成 """
        self.wait.until(EC.visibility_of_element_located(self.COMPLETE_HEADER))

    def get_complete_header(self) -> str:
        """ 完成頁最重要的文字 """
        return self.driver.find_element(*self.COMPLETE_HEADER).text.strip()

    def click_back_home(self):
        """ 點擊回商品列表 """
        self.driver.find_element(*self.BACK_HOME_BTN).click()
