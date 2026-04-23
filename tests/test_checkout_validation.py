import pytest

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


def go_to_checkout_step_one(browser) -> CheckoutPage:
    """登入 -> 加商品 -> 進購物車 -> 進 checkout step 1"""
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(browser)
    inventory_page.wait_for_loaded()
    inventory_page.add_first_item_to_cart()
    inventory_page.go_to_cart()

    cart_page = CartPage(browser)
    cart_page.click_checkout()

    return CheckoutPage(browser)


@pytest.mark.parametrize(
    "first_name,last_name,postal_code,expected_error",
    [
        ("", "User", "10045", "Error: First Name is required"),
        ("Test", "", "10045", "Error: Last Name is required"),
        ("Test", "User", "", "Error: Postal Code is required"),
    ],
    ids=[
        "missing_first_name",
        "missing_last_name",
        "missing_postal_code",
    ],
)
def test_checkout_step_one_required_fields(
    browser, first_name, last_name, postal_code, expected_error
):
    checkout_page = go_to_checkout_step_one(browser)

    # 驗錯誤時要用 submit_step_one，不要用 fill_step_one
    checkout_page.submit_step_one(first_name, last_name, postal_code)

    actual_error = checkout_page.get_error_message()
    assert actual_error == expected_error