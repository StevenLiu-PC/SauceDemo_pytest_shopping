import pytest

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


def go_to_checkout_step_one(browser) -> CheckoutPage:
    """登入 -> 加商品 -> 進 cart -> 進 checkout step 1"""
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
    "first_name,last_name,postal_code,expect_error",
    [
        ("   ", "User", "10045", False),
        ("Test", "   ", "10045", False),
        ("Test", "User", "   ", False),
        ("<script>alert(1)</script>", "User", "10045", False),
        ("12345", "User", "10045", False),
        ("Test", "User", "12AB!", False),
        ("A" * 256, "User", "10045", False),
    ],
    ids=[
        "spaces_only_first_name",
        "spaces_only_last_name",
        "spaces_only_postal_code",
        "script_injection_first_name",
        "numeric_first_name",
        "invalid_postal_code_format",
        "overlong_first_name",
    ],
)
def test_checkout_dirty_data_cases(
    browser, first_name, last_name, postal_code, expect_error
):
    """
    這版先做 UI dirty data 行為觀察：
    - 不預設網站一定會擋
    - 先確認系統不 crash、流程有反應
    - 後續再依實際觀察補 internal control classification
    """
    checkout_page = go_to_checkout_step_one(browser)

    checkout_page.submit_step_one(first_name, last_name, postal_code)

    current_url = browser.current_url
    error_message = checkout_page.get_error_message()

    # 先做最基本驗證：
    # 1. 不是停在空白壞頁
    # 2. 至少要嘛留在 step1 出 error，要嘛進 step2
    assert "checkout-step-one" in current_url or "checkout-step-two" in current_url

    if expect_error:
        assert error_message != ""