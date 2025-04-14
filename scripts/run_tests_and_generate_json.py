import os
import json
import subprocess
from datetime import datetime

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"

# 초기화
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🧹 기존 파일 제거: {path}")

# 테스트 결과 저장 함수
def save_test_result(test_name, message, status="FAIL"):
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []
    results.append(result_data)
    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# 출고 실패 여부 & 스킵 테스트 저장
stock_out_failed = False
skipped_tests = []

# 전체 테스트 목록
all_tests = [
    "tests/test_Bay_login.py",
    "tests/test_Bay_supplier.py",
    "tests/test_Bay_supplier_val.py",
    "tests/test_Bay_supplier_delete.py",
    "tests/test_Bay_prdctg.py",
    "tests/test_Bay_prdctg_val.py",
    "tests/test_Bay_prdctg_edit.py",
    "tests/test_Bay_prdctg_delete.py",
    "tests/test_Bay_product.py",
    "tests/test_Bay_product_val.py",
    "tests/test_Bay_product_edit.py",
    "tests/test_Bay_product_delete_val.py",
    "tests/test_Bay_product_delete.py",
    "tests/test_Bay_stock_in.py",
    "tests/test_Bay_stock_out.py",
    "tests/test_Bay_order_status_request_cancel.py",
    "tests/test_Bay_order_status_request.py",
    "tests/test_Bay_order_status_progress_delivery.py",
    "tests/test_Bay_order_status_progress_complete.py",
    "tests/test_Bay_order_status_delivery.py",
    "tests/test_Bay_order_status_complete.py",
    "tests/test_Bay_order_status_fail.py"
]

# 발주 관련 테스트 목록
order_tests = {
    "tests/test_Bay_order_status_request_cancel.py",
    "tests/test_Bay_order_status_request.py",
    "tests/test_Bay_order_status_progress_delivery.py",
    "tests/test_Bay_order_status_progress_complete.py",
    "tests/test_Bay_order_status_delivery.py",
    "tests/test_Bay_order_status_complete.py",
    "tests/test_Bay_order_status_fail.py"
}

# 테스트 실행
for test_file in all_tests:
    if stock_out_failed and test_file in order_tests:
        print(f"⏭️ 출고 실패로 발주 관련 테스트 스킵: {test_file}")
        skipped_tests.append(test_file)
        save_test_result(
            test_name=os.path.splitext(os.path.basename(test_file))[0],
            message="출고 실패로 인해 발주 테스트 스킵됨",
            status="SKIP"
        )
        continue

    print(f"\n🚀 {test_file} 테스트 실행 중...")
    result = subprocess.run([
        "pytest",
        test_file,
        "--json-report",
        f"--json-report-file={JSON_REPORT_FILE}"
    ])

    test_name = os.path.splitext(os.path.basename(test_file))[0]

    if result.returncode == 0:
        print(f"✅ {test_file} 테스트 완료")
        save_test_result(test_name, "테스트 성공", status="PASS")
    else:
        print(f"❌ {test_file} 테스트 실패")
        save_test_result(test_name, "테스트 실패", status="FAIL")

    if test_file == "tests/test_Bay_stock_out.py":
        if os.path.exists(TEST_RESULTS_FILE):
            with open(TEST_RESULTS_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)
            for r in results:
                if r["test_name"] == "test_stock_outflow" and r["status"] == "FAIL":
                    stock_out_failed = True
                    print("⚠️ 출고 테스트 실패 감지 → 발주 테스트 스킵 모드 활성화")
                    break

# 테스트 완료 후 처리
print("\n🎯 모든 테스트 완료")

if skipped_tests:
    print(f"\n📝 스킵된 테스트: {len(skipped_tests)}개")
    for s in skipped_tests:
        print("•", s)
