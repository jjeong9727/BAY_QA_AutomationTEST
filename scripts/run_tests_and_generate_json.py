import os
import json
import subprocess
from time import sleep

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"

# 실행 전 기존 결과 파일 제거
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🧹 기존 파일 제거: {path}")

# 테스트 목록
test_files = [
    # "tests/test_Bay_login.py",
    # "tests/test_Bay_supplier.py",
    # "tests/test_Bay_supplier_val.py",
    # "tests/test_Bay_supplier_delete.py",
    # "tests/test_Bay_prdctg.py",
    # "tests/test_Bay_prdctg_val.py",
    # "tests/test_Bay_prdctg_edit.py",
    # "tests/test_Bay_prdctg_delete.py",
    # "tests/test_Bay_product.py",
    # "tests/test_Bay_product_val.py",
    # "tests/test_Bay_product_edit.py",
    # "tests/test_Bay_product_delete_val.py",
    # "tests/test_Bay_product_delete.py",
    "tests/test_Bay_stock_in.py",
    "tests/test_Bay_stock_out.py",  # ✅ 이 파일 실패 시 중단
    "tests/test_Bay_order_status_request_cancel.py",
    "tests/test_Bay_order_status_request.py",
    "tests/test_Bay_order_status_progress_delivery.py",
    "tests/test_Bay_order_status_progress_complete.py",
    "tests/test_Bay_order_status_delivery.py",
    "tests/test_Bay_order_status_complete.py",
    "tests/test_Bay_order_status_fail.py"
]

# 테스트 실행
for test_file in test_files:
    print(f"\n🚀 {test_file} 테스트 실행 중...")
    result = subprocess.run([
        "pytest",
        test_file,
        "--json-report",
        f"--json-report-file={JSON_REPORT_FILE}"
    ])

    # if result.returncode == 0:
    #     print(f"✅ {test_file} 테스트 완료")
    # else:
    #     print(f"❌ {test_file} 테스트 실패")

    # 🔎 test_stock_outflow 실패 시 중단
    if test_file == "tests/test_Bay_stock_out.py":
        if os.path.exists(TEST_RESULTS_FILE):
            with open(TEST_RESULTS_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)
            for r in results:
                if r["test_name"] == "test_stock_outflow" and r["status"] == "FAIL":
                    print("⛔ 출고 테스트 실패 감지 → 이후 테스트 중단")
                    exit(1)

print("\n🎯 모든 테스트 완료")
