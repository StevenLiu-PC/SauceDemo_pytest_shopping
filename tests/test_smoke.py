import pytest

from pages.menu_page import MenuPage
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.checkout_page import CheckoutPage
from pages.checkout_complete_page import CheckoutCompletePage


@pytest.fixture(autouse=True)
def smoke_cleanup(browser):
    """
    Smoke 專用保險：
    - conftest 已經做「測試前 reset」
    - 這裡補「測試後 reset」避免 smoke 互相污染
    """
    yield
    try:
        MenuPage(browser).reset_app_state()
    except Exception:
        # 如果測試中 driver 已經異常 / 頁面卡死，避免 cleanup 再噴錯
        pass


@pytest.mark.smoke
def test_smoke_00_login_invalid_shows_error(browser):
    """測試登入失敗會出現錯誤訊息"""
    login = LoginPage(browser)
    login.open()

    login.login("standard_user", "wrong_password")

    msg = login.get_error_text()
    assert "Username and password do not match" in msg


@pytest.mark.smoke
def test_smoke_01_login_to_inventory_items_loaded(inventory_page):
    """測試登入到商品頁後，商品有正常載入"""
    inventory_page.wait_for_loaded()
    items = inventory_page.get_all_items()
    assert len(items) >= 1


@pytest.mark.smoke
def test_smoke_02_add_two_items_and_cart_count_matches(browser, inventory_page):
    """測試加入兩個商品，badge 與購物車數量一致"""
    inventory_page.wait_for_loaded()

    items = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
    for product in items:
        inventory_page.add_item_to_cart_by_name(product)

    assert inventory_page.get_cart_badge_count() == 2

    inventory_page.go_to_cart()
    cart = CartPage(browser)
    assert len(cart.get_item_names()) == 2


@pytest.mark.smoke
def test_smoke_03_sort_dropdown_can_select_lohi(inventory_page):
    """測試商品頁可切換 low to high，且價格順序正確"""
    inventory_page.wait_for_loaded()

    inventory_page.sort_by_value("lohi")
    prices = inventory_page.get_all_prices()

    assert len(prices) >= 2
    assert prices == sorted(prices)


@pytest.mark.smoke
def test_smoke_04_checkout_missing_postal_code_shows_error(browser, inventory_page):
    """測試 checkout 不填 postal code 會出現錯誤訊息"""
    inventory_page.wait_for_loaded()

    inventory_page.add_first_item_to_cart()
    inventory_page.go_to_cart()

    CartPage(browser).click_checkout()

    checkout = CheckoutPage(browser)
    checkout.submit_step_one("Test", "User", "")

    assert "Postal Code is required" in checkout.get_error_message()


@pytest.mark.smoke
def test_smoke_05_complete_page_shows_thank_you(browser, inventory_page):
    """測試完成頁會顯示 Thank you"""
    inventory_page.wait_for_loaded()

    inventory_page.add_first_item_to_cart()
    inventory_page.go_to_cart()

    CartPage(browser).click_checkout()

    checkout = CheckoutPage(browser)
    checkout.fill_step_one("Test", "User", "100")
    checkout.click_finish()

    complete = CheckoutCompletePage(browser)
    complete.wait_for_loaded()
    assert "Thank you" in complete.get_complete_header()