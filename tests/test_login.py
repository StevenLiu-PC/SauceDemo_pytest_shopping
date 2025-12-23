# tests/test_login.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage


class TestLogin:
    """
    SauceDemo 登入測試：
    - 正確帳密 → 登入成功
    - 密碼錯誤 → 顯示錯誤訊息
    """

    def test_login_success_standard_user(self, browser):
        """使用 standard_user / secret_sauce 應該登入成功"""
        page = LoginPage(browser)
        page.open()
        page.login("standard_user", "secret_sauce")

        # 成功登入後網址會包含 /inventory.html
        WebDriverWait(browser, 10).until(
            EC.url_contains("/inventory.html")
        )
        assert "/inventory.html" in browser.current_url

    def test_login_wrong_password(self, browser):
        """帳號對、密碼錯 → 應該顯示錯誤訊息"""
        page = LoginPage(browser)
        page.open()
        page.login("standard_user", "wrong")

        error_text = page.get_error_text().lower()
        # 真正錯誤訊息開一看就知道，可以再調整這裡的字串
        assert "epic sadface" in error_text or "do not match" in error_text

