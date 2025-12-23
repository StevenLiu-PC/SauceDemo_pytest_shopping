# SauceDemo_pytest_shopping

這是一個使用 **pytest + Selenium** 寫的練習專案，  
模擬在 SauceDemo 示範網站上的電商流程：

- 使用者登入
- 瀏覽商品列表
- 加入/移除購物車
- 排序商品
- Checkout（Step 1 → Step 2 → Finish → Complete）
- 必填欄位驗證（Validation）
- 測試狀態隔離（Reset App State）
- 產出 HTML 測試報告（pytest-html）

專案主要目標是練習：

- 如何設計 **UI 自動化測試流程**（Happy path / Cancel branch / Validation）
- 使用 **pytest fixture** 管理共用前置流程（browser / inventory_page）
- 使用 **Page Object Model (POM)** 讓測試程式碼更乾淨、好維護
- 使用 **parametrize** 做資料驅動測試，增加 coverage 但不增加重複碼
- 透過 **Reset App State** 避免測試互相污染，提高穩定性
- 透過 **pytest-html** 產出測試報告
---

## 專案結構

```text
SauceDemo_pytest_shopping
├─ conftest.py                       # browser fixture + inventory_page fixture（登入+reset）
├─ pages/                            # Page Object 目錄
│  ├─ __init__.py
│  ├─ login_page.py                  # LoginPage：登入頁面的操作
│  ├─ inventory_page.py              # InventoryPage：商品列表 + 加入購物車 + 購物車徽章 + 排序
│  ├─ cart_page.py                   # CartPage：購物車頁面商品清單 + 移除 + checkout
│  ├─ checkout_page.py               # CheckoutPage：Step1 填寫/送出 + Step2 finish/cancel + error message
│  ├─ checkout_complete_page.py      # CheckoutCompletePage：完成頁驗證（Thank you...）
│  └─ menu_page.py                   # MenuPage：Reset App State（測試隔離）
├─ tests/                            # 測試案例
│  ├─ __init__.py
│  ├─ test_login.py                  # Day 1：登入相關測試
│  ├─ test_cart_checkout_day3.py     # Day 3：移除商品、排序、checkout step1 → step2
│  ├─ test_checkout_day4.py          # Day 4：Finish 成功、Step2 Cancel、Step1 必填錯誤路徑
│  └─ test_checkout_validation_day5.py # Day 5：parametrize 必填欄位驗證（3 cases）
└─ requirements.txt                  # 套件需求（pytest、selenium）
