from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.checkout_complete_page import CheckoutCompletePage


def login_and_go_inventory(browser) -> InventoryPage:
    """共用前置：登入後進入 inventory 頁"""
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()
    return inventory_page


def go_to_checkout_step_one(browser) -> CheckoutPage:
    """登入 -> 加商品 -> 進 cart -> 進 checkout step 1"""
    inventory_page = login_and_go_inventory(browser)

    inventory_page.add_first_item_to_cart()
    inventory_page.go_to_cart()

    cart_page = CartPage(browser)
    cart_page.click_checkout()

    return CheckoutPage(browser)


def test_checkout_step_one_success(browser):
    """填完 Step 1 後可成功進入 Step 2"""
    checkout_page = go_to_checkout_step_one(browser)

    checkout_page.fill_step_one("Test", "User", "10045")
    assert checkout_page.is_on_step_two()


def test_checkout_finish_success(browser):
    """完整結帳成功後，完成頁顯示 Thank you"""
    checkout_page = go_to_checkout_step_one(browser)

    checkout_page.fill_step_one("Test", "User", "10045")
    checkout_page.click_finish()

    complete_page = CheckoutCompletePage(browser)
    complete_page.wait_for_loaded()

    assert "Thank you" in complete_page.get_complete_header()


def test_checkout_step_two_cancel_back_inventory(browser):
    """Step 2 按 Cancel 後回到 inventory 頁"""
    checkout_page = go_to_checkout_step_one(browser)

    checkout_page.fill_step_one("Test", "User", "10045")
    checkout_page.click_cancel_on_step_two()

    assert "inventory.html" in browser.current_url