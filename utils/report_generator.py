from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


REPORT_DIR = Path("reports/latest")
INPUT_JSON_PATH = REPORT_DIR / "test_results.json"
OUTPUT_MD_PATH = REPORT_DIR / "internal_control_report.md"
OUTPUT_JSON_PATH = REPORT_DIR / "internal_control_report.json"
OUTPUT_CSV_PATH = REPORT_DIR / "test_results_summary.csv"

PROJECT_NAME = "SauceDemo UI Automation Project"
TESTER_NAME = "Steven Liu"


def load_test_results(path: Path) -> list[dict]:
    """讀取 conftest hook 產出的 test_results.json"""
    if not path.exists():
        raise FileNotFoundError(f"找不到測試結果檔案：{path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("test_results.json 格式錯誤，預期應為 list")

    return data


def count_by_key(results: list[dict], key: str) -> dict[str, int]:
    """統計某個欄位的數量"""
    counter = Counter()

    for row in results:
        value = row.get(key, "unknown")
        if not value:
            value = "unknown"
        counter[str(value)] += 1

    return dict(counter)


def build_execution_overview(results: list[dict]) -> dict:
    """建立 Execution Overview"""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    skipped = sum(1 for r in results if r.get("status") == "skipped")

    pass_rate = 0.0
    if total > 0:
        pass_rate = round((passed / total) * 100, 1)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": f"{pass_rate:.1f}%",
    }


def build_scenario_summary(results: list[dict]) -> list[str]:
    """
    Scenario Summary:
    用模組是否出現來列出測試範圍摘要。
    這是測試設計摘要，不是動態結論。
    """
    modules_present = {r.get("module") for r in results}
    summary = []

    if "login" in modules_present:
        summary.append("Login: success, invalid, locked user.")
    if "inventory_cart_flow" in modules_present:
        summary.append("Inventory / Cart: add, remove, badge, sort, navigation.")
    if "checkout_flow" in modules_present:
        summary.append("Checkout Flow: step1, finish, cancel.")
    if "checkout_validation" in modules_present:
        summary.append("Checkout Validation: required fields via pytest.mark.parametrize.")
    if "checkout_dirty_data" in modules_present:
        summary.append("Checkout Dirty Data: abnormal input observation.")
    if "smoke" in modules_present:
        summary.append("Smoke: core path.")
    if "stress" in modules_present:
        summary.append("Stress: repetitive UI stability.")

    return summary


def build_breakdown(results: list[dict]) -> dict:
    """建立 Breakdown"""
    by_module = count_by_key(results, "module")
    by_test_type = count_by_key(results, "test_type")

    by_result = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
    }
    actual_result = count_by_key(results, "status")
    for key, value in actual_result.items():
        by_result[key] = value

    return {
        "by_module": by_module,
        "by_test_type": by_test_type,
        "by_result": by_result,
    }


def build_evidence_outputs() -> list[str]:
    """Evidence & Outputs 固定列出報告產物項目"""
    return [
        "Pytest HTML report",
        "Allure results",
        "Screenshots on failure",
        "Internal control outputs (.md / .json / .csv)",
    ]


def build_report_payload(results: list[dict]) -> dict:
    """整合成報告資料（純購物車專案版，無 DDE）"""
    return {
        "project": PROJECT_NAME,
        "tester": TESTER_NAME,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "execution_overview": build_execution_overview(results),
        "scenario_summary": build_scenario_summary(results),
        "breakdown": build_breakdown(results),
        "evidence_outputs": build_evidence_outputs(),
    }


def render_markdown(payload: dict) -> str:
    """輸出 internal_control_report.md"""
    overview = payload["execution_overview"]
    breakdown = payload["breakdown"]

    lines: list[str] = []

    lines.append("# Internal Control Report")
    lines.append("")
    lines.append(f"- Project: {payload['project']}")
    lines.append(f"- Tester: {payload['tester']}")
    lines.append(f"- Generated At: {payload['generated_at']}")
    lines.append("")

    lines.append("## Execution Overview")
    lines.append("")
    lines.append(f"- Total: {overview['total']}")
    lines.append(f"- Passed: {overview['passed']}")
    lines.append(f"- Failed: {overview['failed']}")
    lines.append(f"- Skipped: {overview['skipped']}")
    lines.append(f"- Pass Rate: {overview['pass_rate']}")
    lines.append("")

    lines.append("## Scenario Summary")
    lines.append("")
    for item in payload["scenario_summary"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Breakdown")
    lines.append("")

    lines.append("### By Module")
    lines.append("")
    for key, value in breakdown["by_module"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("### By Test Type")
    lines.append("")
    for key, value in breakdown["by_test_type"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("### By Result")
    lines.append("")
    for key, value in breakdown["by_result"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Evidence & Outputs")
    lines.append("")
    for item in payload["evidence_outputs"]:
        lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, payload: dict) -> None:
    """輸出 internal_control_report.json"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_markdown(path: Path, content: str) -> None:
    """輸出 internal_control_report.md"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def write_summary_csv(path: Path, payload: dict) -> None:
    """輸出 summary csv"""
    overview = payload["execution_overview"]
    breakdown = payload["breakdown"]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "item", "value"])

        # Execution Overview
        for key, value in overview.items():
            writer.writerow(["execution_overview", key, value])

        # Scenario Summary
        for item in payload["scenario_summary"]:
            writer.writerow(["scenario_summary", "item", item])

        # Breakdown
        for key, value in breakdown["by_module"].items():
            writer.writerow(["breakdown_by_module", key, value])

        for key, value in breakdown["by_test_type"].items():
            writer.writerow(["breakdown_by_test_type", key, value])

        for key, value in breakdown["by_result"].items():
            writer.writerow(["breakdown_by_result", key, value])

        # Evidence
        for item in payload["evidence_outputs"]:
            writer.writerow(["evidence_outputs", "item", item])


def main() -> None:
    results = load_test_results(INPUT_JSON_PATH)
    payload = build_report_payload(results)
    markdown = render_markdown(payload)

    write_json(OUTPUT_JSON_PATH, payload)
    write_markdown(OUTPUT_MD_PATH, markdown)
    write_summary_csv(OUTPUT_CSV_PATH, payload)

    print("Report generated:")
    print(f"- {OUTPUT_MD_PATH}")
    print(f"- {OUTPUT_JSON_PATH}")
    print(f"- {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()