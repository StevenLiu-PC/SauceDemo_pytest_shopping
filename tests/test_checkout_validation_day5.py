import pytest
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

@pytest.mark.parametrize(
    "first_name,last_name,postal,expected",
    [
        ("", "User", "10045", "First Name is required"),
        ("Test", "", "10045", "Last Name is required"),
        ("Test", "User", "", "Postal Code is required"),
    ]
)
def test_checkout_step_one_required_fields(inventory_page, browser, first_name, last_name, postal, expected):
    # inventory_page 已登入且 reset 過
    """ 先把商品加進購物車，再進購物車頁 """
    inventory_page.add_first_item_to_cart()
    inventory_page.go_to_cart()
    """ 在購物車頁點 Checkout 進入結帳 Step 1 """
    cart_page = CartPage(browser)
    cart_page.click_checkout()
    """ 在 Step 1 輸入資料並送出（故意缺一欄） """
    checkout_page = CheckoutPage(browser)
    checkout_page.submit_step_one(first_name, last_name, postal)
    """ 抓錯誤訊息，確認包含預期的句子 """
    msg = checkout_page.get_error_message()
    assert expected in msg
