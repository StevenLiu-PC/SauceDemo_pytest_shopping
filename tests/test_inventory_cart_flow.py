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


def test_open_first_item_and_back(browser):
    """進第一個商品詳細頁，再返回商品列表"""
    inventory_page = login_and_go_inventory(browser)

    inventory_page.open_first_item()

    title = inventory_page.get_detail_title()
    assert title != ""

    inventory_page.click_back_to_products()
    assert "inventory.html" in browser.current_url


def test_add_one_item_shows_badge_and_cart(browser):
    """加入一個商品後，badge 與 cart 內容正確"""
    inventory_page = login_and_go_inventory(browser)

    inventory_page.add_first_item_to_cart()

    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.go_to_cart()
    cart_page = CartPage(browser)

    item_names = cart_page.get_item_names()
    assert len(item_names) >= 1


def test_add_two_specific_items_and_verify(browser):
    """加入兩個指定商品，badge 與 cart 內容正確"""
    target_items = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]

    inventory_page = login_and_go_inventory(browser)

    for name in target_items:
        inventory_page.add_item_to_cart_by_name(name)

    assert inventory_page.get_cart_badge_count() == 2

    inventory_page.go_to_cart()
    cart_page = CartPage(browser)

    item_names = cart_page.get_item_names()
    for name in target_items:
        assert name in item_names


@pytest.mark.parametrize(
    "target_items,expected_remaining_count",
    [
        (["Sauce Labs Backpack", "Sauce Labs Bike Light"], 1),
        (
            [
                "Sauce Labs Backpack",
                "Sauce Labs Bike Light",
                "Sauce Labs Bolt T-Shirt",
            ],
            2,
        ),
    ],
    ids=[
        "remove_from_two_items",
        "remove_from_three_items",
    ],
)
def test_remove_item_from_cart(browser, target_items, expected_remaining_count):
    """加入多個商品後移除第一個，確認剩餘數量正確"""
    inventory_page = login_and_go_inventory(browser)

    for name in target_items:
        inventory_page.add_item_to_cart_by_name(name)

    assert inventory_page.get_cart_badge_count() == len(target_items)

    inventory_page.go_to_cart()
    cart_page = CartPage(browser)

    item_names_before = cart_page.get_item_names()
    assert len(item_names_before) == len(target_items)

    cart_page.remove_first_item()

    item_names_after = cart_page.get_item_names()
    assert len(item_names_after) == expected_remaining_count


@pytest.mark.parametrize(
    "sort_value,sort_mode",
    [
        ("lohi", "ascending"),
        ("hilo", "descending"),
    ],
    ids=[
        "sort_low_to_high",
        "sort_high_to_low",
    ],
)
def test_sort_items_by_price(browser, sort_value, sort_mode):
    """驗證商品價格排序功能正常"""
    inventory_page = login_and_go_inventory(browser)

    inventory_page.sort_by_value(sort_value)
    prices = inventory_page.get_all_prices()

    assert len(prices) >= 2

    if sort_mode == "ascending":
        assert prices == sorted(prices)
    else:
        assert prices == sorted(prices, reverse=True)