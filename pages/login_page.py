from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """
    SauceDemo 登入頁的 Page Object
    - 負責「打開登入頁」跟「輸入帳密登入」
    """

    URL = "https://www.saucedemo.com/"
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR_MSG = (By.CSS_SELECTOR, "h3[data-test='error']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self) -> None:
        """打開登入頁"""
        self.driver.get(self.URL)

    def login(self, username: str, password: str) -> None:
        """輸入帳密並送出（只做操作，不做斷言）"""
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BTN).click()

    def get_error_text(self) -> str:
        """取得登入失敗時的錯誤訊息文字"""
        error_el = self.wait.until(
            EC.visibility_of_element_located(self.ERROR_MSG)
        )
        return error_el.text.strip()
    def login_as_standard_user(self):
        self.open()
        self.login("standard_user", "secret_sauce")