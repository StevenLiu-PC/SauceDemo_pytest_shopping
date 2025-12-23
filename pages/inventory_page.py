from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


class InventoryPage:
    """
    商品列表頁 Page Object：
    - 等商品載入
    - 點第一個商品
    - 讀取商品詳細頁標題
    - 點 Back to products 回列表
    """

    INVENTORY_ITEM = (By.CLASS_NAME, "inventory_item")
    INVENTORY_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    DETAIL_TITLE = (By.CLASS_NAME, "inventory_details_name")
    BACK_TO_PRODUCTS_BTN = (By.ID, "back-to-products")
    INVENTORY_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    # 購物車元素
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button.btn_inventory")

    SORT_SELECT = (By.CLASS_NAME, "product_sort_container")
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_for_loaded(self) -> None:
        """等待商品列表至少出現一個商品"""
        self.wait.until(
            EC.visibility_of_element_located(self.INVENTORY_ITEM)
        )
    def get_all_items(self):
        """回傳目前列表上的所有商品元素 list[WebElement]"""
        return self.driver.find_elements(*self.INVENTORY_ITEM)

    def open_first_item(self) -> None:
        """點列表中的第一個商品名稱，進入詳細頁"""
        first_name_el = self.driver.find_elements(*self.INVENTORY_ITEM_NAME)[0]
        first_name_el.click()

    def get_detail_title(self) -> str:
        """取得商品詳細頁的標題文字"""
        title_el = self.wait.until(
            EC.visibility_of_element_located(self.DETAIL_TITLE)
        )
        return title_el.text.strip()

    def click_back_to_products(self) -> None:
        """從商品詳細頁點 Back to products 回到列表"""
        btn = self.wait.until(
            EC.element_to_be_clickable(self.BACK_TO_PRODUCTS_BTN)
        )
        btn.click()


        """ 購物車 """
    def add_first_item_to_cart(self):
        """在列表頁把第一個商品加入購物車"""
        first_btn = self.driver.find_elements(*self.ADD_TO_CART_BUTTONS)[0]
        first_btn.click()

    def add_item_to_cart_by_name(self, name: str):
        """
        根據商品名稱加入購物車：
        - 找到商品區塊
        - 比對名稱
        - 點該區塊底下的按鈕
        """
        items = self.driver.find_elements(*self.INVENTORY_ITEM)
        for item in items:
            title_el = item.find_element(*self.INVENTORY_ITEM_NAME)
            if title_el.text.strip() == name:
                button_el = item.find_element(By.CSS_SELECTOR, "button.btn_inventory")
                button_el.click()
                return
        # 如果這一圈都沒找到，直接丟錯比較好除錯
        raise AssertionError(f"找不到商品：{name}")

    def get_cart_badge_count(self) -> int:
        """
        回傳購物車徽章上的數字沒有徽章時回傳 0
        """
        try:
            badge = self.driver.find_element(*self.CART_BADGE)
            return int(badge.text.strip())
        except NoSuchElementException:
            return 0

    def go_to_cart(self):
        """點右上角購物車 icon 進入購物車頁"""
        cart_link = self.wait.until(
            EC.element_to_be_clickable(self.CART_LINK)
        )
        cart_link.click()
    def sort_by_value(self, value: str) -> None:
        """根據 select 的 value 進行排序，例如 'lohi', 'hilo'"""
        select_el = self.wait.until(
            EC.presence_of_element_located(self.SORT_SELECT)
        )
        select = Select(select_el)
        select.select_by_value(value)

    def get_all_prices(self):
        """取得目前列表上的所有商品價格 list[float]"""
        price_elems = self.driver.find_elements(*self.INVENTORY_ITEM_PRICE)
        prices = []
        for el in price_elems:
            text = el.text.replace("$", "").strip()
            prices.append(float(text))
        return prices