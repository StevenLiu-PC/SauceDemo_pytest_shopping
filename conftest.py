import csv
import json
import os
import re
import subprocess
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.menu_page import MenuPage


REPORT_LATEST_DIR = Path("reports/latest")
SCREENSHOT_DIR = Path("reports/screenshots")
RESULT_JSON_PATH = REPORT_LATEST_DIR / "test_results.json"
RESULT_CSV_PATH = REPORT_LATEST_DIR / "test_results.csv"


def _safe_name(name: str) -> str:
    """把字串轉成安全檔名"""
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)


def _ensure_report_dirs() -> None:
    """建立報告資料夾"""
    REPORT_LATEST_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _infer_module_from_nodeid(nodeid: str) -> str:
    """
    依 nodeid 推測模組名稱
    例如:
    tests/test_login.py::test_login_success_standard_user
    """
    nodeid_lower = nodeid.lower()

    if "test_login.py" in nodeid_lower:
        return "login"
    if "test_inventory_cart_flow.py" in nodeid_lower:
        return "inventory_cart_flow"
    if "test_checkout_flow.py" in nodeid_lower:
        return "checkout_flow"
    if "test_checkout_validation.py" in nodeid_lower:
        return "checkout_validation"
    if "test_checkout_dirty_data.py" in nodeid_lower:
        return "checkout_dirty_data"
    if "test_smoke.py" in nodeid_lower:
        return "smoke"
    if "test_stress.py" in nodeid_lower:
        return "stress"

    return "unknown"


def _infer_test_type(module: str, test_name: str) -> str:
    """
    依模組 + 測試名稱推測 test type
    login 需要特別拆：
    - success -> positive_flow
    - 其餘 login negative cases -> negative_validation
    """
    if module == "login":
        if "success" in test_name.lower():
            return "positive_flow"
        return "negative_validation"

    mapping = {
        "inventory_cart_flow": "positive_flow",
        "checkout_flow": "positive_flow",
        "checkout_validation": "negative_validation",
        "checkout_dirty_data": "dirty_data_observation",
        "smoke": "smoke_gate",
        "stress": "stress_stability",
        "unknown": "unknown",
    }
    return mapping.get(module, "unknown")


def _write_test_results_json(results: list[dict]) -> None:
    with open(RESULT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def _write_test_results_csv(results: list[dict]) -> None:
    with open(RESULT_CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "test_name",
                "nodeid",
                "module",
                "test_type",
                "status",
                "duration",
                "screenshot_path",
                "url_path",
            ]
        )

        for row in results:
            writer.writerow(
                [
                    row.get("test_name", ""),
                    row.get("nodeid", ""),
                    row.get("module", ""),
                    row.get("test_type", ""),
                    row.get("status", ""),
                    row.get("duration", 0),
                    row.get("screenshot_path", ""),
                    row.get("url_path", ""),
                ]
            )


@pytest.fixture(scope="session", autouse=True)
def test_result_store():
    """
    全 session 共用的測試結果收集器
    pytest 執行期間，每支 test 的結果都 append 進來
    session 結束後：
    1. 輸出 test_results.json / csv
    2. 自動執行 report_generator.py
    """
    _ensure_report_dirs()
    results = []
    yield results

    # 先輸出原始測試結果
    _write_test_results_json(results)
    _write_test_results_csv(results)

    # 再自動產生內控報告
    try:
        subprocess.run(
            ["python", "utils/report_generator.py"],
            check=True,
        )
        print("Internal control report generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate internal control report: {e}")


@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--lang=en-US")

    # 關掉密碼相關提示，避免干擾 UI
    prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--guest")

    # CI 才開 headless；本機維持正常視窗
    if (
        os.getenv("CI", "").lower() == "true"
        or os.getenv("HEADLESS", "").lower() == "true"
    ):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    yield driver
    driver.quit()


@pytest.fixture
def inventory_page(browser):
    """
    可重複使用的入口：
    登入 -> 到 inventory -> reset app state
    """
    login_page = LoginPage(browser)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    inventory = InventoryPage(browser)
    inventory.wait_for_loaded()

    # 狀態隔離：每支測試開始前先 reset
    MenuPage(browser).reset_app_state()

    return inventory


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    每支測試執行後：
    1. 收集結果
    2. 若失敗則截圖
    """
    outcome = yield
    report = outcome.get_result()

    # 只處理測試主體（call），不處理 setup / teardown
    if report.when != "call":
        return

    # 取得共用結果收集器
    result_store = item.funcargs.get("test_result_store", None)
    if result_store is None:
        return

    driver = item.funcargs.get("browser", None)

    screenshot_path = ""
    url_path = ""

    status = "passed"
    if report.failed:
        status = "failed"
    elif report.skipped:
        status = "skipped"

    # 失敗才截圖
    if report.failed and driver is not None:
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = _safe_name(f"{ts}_{item.name}.png")
        screenshot_file = SCREENSHOT_DIR / filename

        try:
            driver.save_screenshot(str(screenshot_file))
            screenshot_path = str(screenshot_file).replace("\\", "/")

            url_file = SCREENSHOT_DIR / _safe_name(f"{ts}_{item.name}.url.txt")
            with open(url_file, "w", encoding="utf-8") as f:
                f.write(getattr(driver, "current_url", ""))
            url_path = str(url_file).replace("\\", "/")
        except WebDriverException:
            pass

    nodeid = item.nodeid
    module = _infer_module_from_nodeid(nodeid)
    test_type = _infer_test_type(module, item.name)

    result_store.append(
        {
            "test_name": item.name,
            "nodeid": nodeid,
            "module": module,
            "test_type": test_type,
            "status": status,
            "duration": round(getattr(report, "duration", 0.0), 4),
            "screenshot_path": screenshot_path,
            "url_path": url_path,
        }
    )