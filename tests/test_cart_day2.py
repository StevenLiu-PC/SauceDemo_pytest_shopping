from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


def test_add_one_item_shows_badge_and_cart(browser):
    """
    Day 2 - 測試 1：
    1. 登入 standard_user
    2. 等商品列表載入
    3. 把第一個商品加入購物車
    4. 驗證右上角購物車徽章顯示 1
    5. 進購物車頁，驗證裡面至少有 1 個商品
    """
    # 登入
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()

    # 加入第一個商品
    inventory_page.add_first_item_to_cart()

    # 驗證徽章顯示 1
    badge_count = inventory_page.get_cart_badge_count()
    assert badge_count == 1

    # 進購物車頁
    inventory_page.go_to_cart()

    # 驗證購物車裡真的有東西
    cart_page = CartPage(browser)
    item_names = cart_page.get_item_names()
    assert len(item_names) >= 1


def test_add_two_specific_items_and_verify(browser):
    """
    Day 2 測試 
    1. 登入 standard_user
    2. 加入兩個特定商品：
       - Sauce Labs Backpack
       - Sauce Labs Bike Light
    3. 驗證徽章顯示 2
    4. 進購物車頁，確認這兩個商品名稱都有出現
    """
    target_items = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]

    # 登入
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()

    # 加入兩個指定商品
    for name in target_items:
        inventory_page.add_item_to_cart_by_name(name)

    # 驗證徽章顯示 2
    badge_count = inventory_page.get_cart_badge_count()
    assert badge_count == 2

    # 進購物車頁
    inventory_page.go_to_cart()
    cart_page = CartPage(browser)
    item_names = cart_page.get_item_names()

    # 驗證兩個商品都在購物車清單裡
    for name in target_items:
        assert name in item_names
