from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.checkout_complete_page import CheckoutCompletePage

class TestShopDay4:
    def login_and_go_inventory(self, browser):
        login_page = LoginPage(browser)
        login_page.open()
        login_page.login("standard_user", "secret_sauce")

        inventory_page = InventoryPage(browser)
        inventory_page.wait_for_loaded()
        return inventory_page
    
    def go_to_checkout_step_one(self, browser) -> CheckoutPage:
        """ 共用前置：登入 """ 
        inventory_page = self.login_and_go_inventory(browser)
        """ 加入商品 + 進購物車 """
        inventory_page.add_first_item_to_cart()
        inventory_page.go_to_cart()
        """ 在購物車頁點 checkout """
        cart_page = CartPage(browser)
        cart_page.click_checkout()
        """ 進 Step1 回傳 CheckoutPage """
        return CheckoutPage(browser)

    def test_checkout_finish_success(self, browser):
        """成功結帳最重要主流程"""
        checkout_page = self.go_to_checkout_step_one(browser)

        checkout_page.fill_step_one("Test", "User", "10045")
        checkout_page.click_finish()

        complete_page = CheckoutCompletePage(browser)
        complete_page.wait_for_loaded()
        assert "Thank you" in complete_page.get_complete_header()

    def test_checkout_step_two_cancel_back_inventory(self, browser):
        """Step2 Cancel 回 inventory測分支與狀態"""
        checkout_page = self.go_to_checkout_step_one(browser)

        checkout_page.fill_step_one("Test", "User", "10045")
        checkout_page.click_cancel_on_step_two()
        """ 確認回到商品列表頁 """
        assert "inventory.html" in browser.current_url

    def test_checkout_step_one_missing_postal_code_shows_error(self, browser):
        """Step1 少填必填欄位會出錯（測防呆）"""
        checkout_page = self.go_to_checkout_step_one(browser)
        checkout_page.submit_step_one("Test", "User", "")  # 故意不填 postal code
        """ 確認系統有擋、也有提示使用者 """
        assert "Postal Code is required" in checkout_page.get_error_message()
