import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.menu_page import MenuPage
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--lang=en-US")
    prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--guest")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    yield driver

    driver.quit()
@pytest.fixture
def inventory_page(browser):
    """
    Day5 fixture
    - 登入 standard_user
    - 進 inventory
    - reset app state確保每支測試互不污染
    - 回傳 InventoryPage 物件
    """
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory = InventoryPage(browser)
    inventory.wait_for_loaded()

    # 狀態隔離：每支測試開始前先 reset（清購物車/狀態）
    MenuPage(browser).reset_app_state()

    return inventory