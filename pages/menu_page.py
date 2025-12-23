from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MenuPage:
    MENU_BTN = (By.ID, "react-burger-menu-btn")
    RESET_LINK = (By.ID, "reset_sidebar_link")
    CLOSE_BTN = (By.ID, "react-burger-cross-btn")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def reset_app_state(self):
        """打開側欄 → Reset App State → 關閉側欄"""
        self.wait.until(EC.element_to_be_clickable(self.MENU_BTN)).click()
        self.wait.until(EC.element_to_be_clickable(self.RESET_LINK)).click()
        self.wait.until(EC.element_to_be_clickable(self.CLOSE_BTN)).click()
