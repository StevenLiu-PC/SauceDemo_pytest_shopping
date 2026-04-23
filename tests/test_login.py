import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage


@pytest.mark.parametrize(
    "username,password,expected_error",
    [
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("", "", "Username is required"),
        ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out"),
    ],
    ids=[
        "wrong_password",
        "empty_username",
        "empty_password",
        "empty_both",
        "locked_out_user",
    ],
)
def test_login_negative_cases(browser, username, password, expected_error):
    """登入負向案例矩陣"""
    login = LoginPage(browser)
    login.open()
    login.login(username, password)

    msg = login.get_error_text()
    assert expected_error in msg


def test_login_success_standard_user(browser):
    """成功登入 standard_user 後進入 inventory 頁"""
    login = LoginPage(browser)
    login.open()
    login.login("standard_user", "secret_sauce")

    WebDriverWait(browser, 10).until(EC.url_contains("inventory.html"))
    assert "inventory.html" in browser.current_url