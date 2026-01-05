import pytest
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from pages.menu_page import MenuPage
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

# 把字串變成可以當檔名的形式
def _safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)

@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--lang=en-US")

    # 關掉密碼相關提示（避免干擾 UI）
    prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--guest")
    # CI 才開 headless（本機就正常開視窗）
    if os.getenv("CI", "").lower() == "true":
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
    # 建 driver，並關掉 implicit wait    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    yield driver

    driver.quit()

@pytest.fixture
def inventory_page(browser):

    # 把「登入→到商品頁→reset」變成一個可重用的入口

    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory = InventoryPage(browser)
    inventory.wait_for_loaded()

    # 狀態隔離：每支測試開始前先 reset（清購物車/狀態）
    MenuPage(browser).reset_app_state()

    return inventory


@pytest.hookimpl(hookwrapper=True)  # 失敗才截圖
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or report.passed: # 只截「測試本體 call」失敗
        return
    # 取得 driver
    driver = item.funcargs.get("browser", None)
    if driver is None:
        return
    # 建立資料夾 + 產檔名
    os.makedirs("reports/screenshots", exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = _safe_name(f"{ts}_{item.name}.png")
    path = os.path.join("reports", "screenshots", filename)

    try:
        driver.save_screenshot(path) # 截圖 + 存 URL
        url_path = os.path.join("reports", "screenshots", _safe_name(f"{ts}_{item.name}.url.txt"))
        with open(url_path, "w", encoding="utf-8") as f:
            f.write(getattr(driver, "current_url", ""))
    except WebDriverException:
        pass