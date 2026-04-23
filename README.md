# SauceDemo_pytest_shopping

這是一個使用 **pytest + Selenium** 撰寫的 UI 自動化測試專案，  
模擬 SauceDemo 示範網站上的電商流程，並延伸加入：

- Validation
- Dirty Data Observation
- Stress
- 測試結果收集
- 自動產出內控驗證報告
- Allure 結果輸出

---

## 專案目標

- 設計 **黑箱 UI 自動化測試流程**
- 使用 **pytest fixture** 管理共用前置流程
- 使用 **Page Object Model (POM)** 提高可維護性
- 使用 **parametrize** 增加資料覆蓋但不增加重複碼
- 透過 **Reset App State** 避免測試互相污染
- 透過 **conftest hook** 收集測試結果、失敗截圖與網址
- 透過 **report_generator.py** 自動產出內控驗證報告
- 透過 **Allure** 保留測試結果與證據
