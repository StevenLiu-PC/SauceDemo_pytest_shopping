import pytest

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


def login_and_go_inventory(browser) -> InventoryPage:
    """共用前置：登入後進入 inventory 頁"""
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()
    return inventory_page


@pytest.mark.stress
def test_stress_repeated_add_remove_cart(browser):
    """
    重複加購 / 移除購物車穩定性測試
    驗證多輪操作後 badge 與 cart 狀態仍一致
    """
    inventory_page = login_and_go_inventory(browser)
    target_item = "Sauce Labs Backpack"

    for _ in range(5):
        inventory_page.add_item_to_cart_by_name(target_item)
        assert inventory_page.get_cart_badge_count() == 1

        inventory_page.go_to_cart()
        cart_page = CartPage(browser)

        item_names = cart_page.get_item_names()
        assert target_item in item_names
        assert len(item_names) == 1

        cart_page.remove_first_item()

        remaining_items = cart_page.get_item_names()
        assert len(remaining_items) == 0

        browser.back()
        inventory_page.wait_for_loaded()


@pytest.mark.stress
def test_stress_repeated_sort_switch(browser):
    """
    重複切換排序穩定性測試
    驗證連續切換 low->high / high->low 後價格仍正確
    """
    inventory_page = login_and_go_inventory(browser)

    for _ in range(5):
        inventory_page.sort_by_value("lohi")
        prices_low_high = inventory_page.get_all_prices()
        assert prices_low_high == sorted(prices_low_high)

        inventory_page.sort_by_value("hilo")
        prices_high_low = inventory_page.get_all_prices()
        assert prices_high_low == sorted(prices_high_low, reverse=True)


@pytest.mark.stress
def test_stress_repeated_open_detail_and_back(browser):
    """
    重複開商品詳情頁再返回穩定性測試
    驗證多輪進出後仍可正常回到 inventory
    """
    inventory_page = login_and_go_inventory(browser)

    for _ in range(5):
        inventory_page.open_first_item()

        title = inventory_page.get_detail_title()
        assert title != ""

        inventory_page.click_back_to_products()
        assert "inventory.html" in browser.current_url

        inventory_page.wait_for_loaded()