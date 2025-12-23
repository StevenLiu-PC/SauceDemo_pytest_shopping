from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

class TestShopDay3:
    def login_and_go_inventory(self, browser):
        """小工具：登入 standard_user 回傳 inventory_page 物件"""
        login_page = LoginPage(browser)
        login_page.open()
        login_page.login("standard_user", "secret_sauce")

        inventory_page = InventoryPage(browser)
        inventory_page.wait_for_loaded()
        return inventory_page


    def test_remove_item_from_cart(self,browser):
        """Day 3 測試 1 加入兩個商品後，移除一個"""
        inventory_page = self.login_and_go_inventory(browser)
        """ 指定要加哪兩個商品 """
        target_items = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
        for name in target_items:
            inventory_page.add_item_to_cart_by_name(name)
        """ 第一個驗證：購物車徽章應該顯示 2 """
        assert inventory_page.get_cart_badge_count() == 2
        """ 進購物車頁面，驗證購物車清單真的有 2 個 """
        inventory_page.go_to_cart()
        cart_page = CartPage(browser)
        """ 抓購物車裡所有商品名稱回傳 list """
        item_names_before = cart_page.get_item_names()
        assert len(item_names_before) == 2
        """ 動作：移除第一個商品 """
        cart_page.remove_first_item()
        """ 移除後剩 1 個 """
        item_names_after = cart_page.get_item_names()
        """ 驗證 remove 功能有效 """
        assert len(item_names_after) == 1


    def test_sort_items_low_to_high(self, browser):
        """Day 3 測試 2 使用價格由低到高排序，驗證價格順序"""
        inventory_page = self.login_and_go_inventory(browser)
        """ 排序值low to high """
        inventory_page.sort_by_value("lohi")
        """ 把頁面上所有商品價格抓出來 """
        sorted_prices = inventory_page.get_all_prices()
        """ 驗證：頁面上的價格順序要等於由小到大排序後的結果 """
        assert sorted_prices == sorted(sorted_prices)


    def test_checkout_step_one_success(self, browser):
        """Day 3 測試 3 加入一個商品 → 購物車 → 結帳 Step 1 填寫成功"""
        inventory_page = self.login_and_go_inventory(browser)
        # 加入一個商品
        inventory_page.add_first_item_to_cart()
        assert inventory_page.get_cart_badge_count() == 1
        # 進購物車頁面
        inventory_page.go_to_cart()
        cart_page = CartPage(browser)
        # 確認購物車裡有 1 個商品
        item_names = cart_page.get_item_names()
        assert len(item_names) == 1
        # 點 Checkout 進入結帳頁面 (Step 1)
        cart_page.click_checkout()
        # 填 Step 1 資料
        checkout_page = CheckoutPage(browser)
        checkout_page.fill_step_one("Test", "User", "10045")
        # 驗證已到 Step 2
        assert checkout_page.is_on_step_two()