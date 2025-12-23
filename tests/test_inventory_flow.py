# tests/test_inventory_flow.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_open_first_item_and_back(browser):
    """
    流程：
    1. 使用 standard_user 登入
    2. 等商品列表載入
    3. 點第一個商品進詳細頁
    4. 驗證詳細頁標題不是空的
    5. 點 Back to products 回列表
    6. 驗證網址回到 /inventory.html
    """
    # Step 1: 先登入
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    # Step 2: 等商品列表載入
    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()

    # Step 3: 點第一個商品
    inventory_page.open_first_item()

    # Step 4: 驗證詳細頁有標題
    title = inventory_page.get_detail_title()
    assert title != ""

    # Step 5: 點 Back to products
    inventory_page.click_back_to_products()

    # Step 6: 驗證回到 /inventory.html
    WebDriverWait(browser, 10).until(
        EC.url_contains("/inventory.html")
    )
    assert "/inventory.html" in browser.current_url

