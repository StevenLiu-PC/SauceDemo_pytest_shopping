from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os 


class CartPage:
    """
    購物車頁面 Page Object
    - 讀取購物車裡的商品名稱清單
    """
    CART_ITEM = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    CART_ITEM_REMOVE_BTN = (By.CSS_SELECTOR, "button.cart_button")
    CHECKOUT_BTN = (By.ID, "checkout")
    CART_CONTAINER = (By.ID, "cart_contents_container")
    

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_item_names(self):
        """回傳購物車裡所有商品名稱list[str]"""
        self.wait.until(EC.presence_of_element_located(self.CART_CONTAINER))
        elems = self.driver.find_elements(*self.CART_ITEM_NAME)
        return [el.text.strip() for el in elems]
    
    def remove_first_item(self):
        """移除購物車中的第一個商品"""
        # 確保 cart_item 出現
        self.wait.until(EC.presence_of_all_elements_located(self.CART_ITEM))
        items_before = self.driver.find_elements(*self.CART_ITEM)

        if not items_before:
            raise AssertionError("購物車沒有可移除的商品")

        before_count = len(items_before)

        # 在第一個 cart_item裡面找 Remove，避免 selector 太廣點到怪東西
        first_item = items_before[0]
        first_item.find_element(*self.CART_ITEM_REMOVE_BTN).click()

        #  關鍵：等到 cart_item 數量真的 -1（DOM 更新完）
        self.wait.until(lambda d: len(d.find_elements(*self.CART_ITEM)) == before_count - 1)
    
    def click_checkout(self):
        """點擊 Checkout 按鈕，進入結帳流程"""
        btn = self.wait.until(EC.element_to_be_clickable(self.CHECKOUT_BTN))
        btn.click()
        try:
            self.wait.until(EC.url_contains("checkout-step-one"))
            """ 如果等不到：做 debug 訊息 + 截圖 + 把錯誤丟回去 """
        except TimeoutException:
            print("DEBUG click_checkout failed, current url =", self.driver.current_url)
            os.makedirs("reports/screenshots", exist_ok=True)
            self.driver.save_screenshot("debug_click_checkout_timeout.png")
            raise