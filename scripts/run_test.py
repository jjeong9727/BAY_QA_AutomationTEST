import os
import json
import subprocess
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from helpers.common_utils import clean_product_json

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"

# 초기화
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🪩 기존 파일 제거: {path}")

clean_product_json()

def save_test_result(test_name, message, status="FAIL", file_name=None, stack_trace="", duration=None):
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": file_name,
        "stack": stack_trace,
        "duration": duration
    }

    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    results.append(result_data)

    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# 전체 테스트 목록
all_tests = [
    "tests/test_Bay_login.py",
    "tests/test_Bay_alert.py",
    "tests/test_Bay_supplier.py",
    "tests/test_Bay_category.py",
    "tests/test_Bay_rule_order.py",
    "tests/test_Bay_rule_approval.py",
    "tests/test_Bay_product.py",
    "tests/test_Bay_product_upload_validation.py",
    "tests/test_Bay_product_upload.py",
    "tests/test_Bay_rule_order_apply_bulk.py",
    "tests/test_Bay_product_edit.py",
    "tests/test_Bay_stock_in.py",
    "tests/test_Bay_stock_out.py",
    "tests/test_Bay_order_pending.py",
    "tests/test_Bay_order_approval.py",
    "tests/test_Bay_order_status.py",
    "tests/test_Bay_order_status_batch.py",
    "tests/test_Bay_stock_history.py",
]

# 테스트 실행
for test_file in all_tests:
    print(f"\n🚀 {test_file} 테스트 실행 중...")
    start_time = datetime.now()
    try:
        subprocess.run(
            ["pytest", test_file, "--json-report", f"--json-report-file={JSON_REPORT_FILE}"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ {test_file} 테스트 실패")
    finally:
        duration = (datetime.now() - start_time).total_seconds()

        # pytest 결과 파일 확인
        if os.path.exists(JSON_REPORT_FILE):
            with open(JSON_REPORT_FILE, "r", encoding="utf-8") as f:
                report = json.load(f)

            if "tests" in report:
                pass_cnt = sum(1 for t in report["tests"] if t.get("outcome") == "passed")
                fail_cnt = sum(1 for t in report["tests"] if t.get("outcome") == "failed")
                skip_cnt = sum(1 for t in report["tests"] if t.get("outcome") == "skipped")

                # ✅ 파일 단위 결과 로그 추가
                print(f"✅ {test_file} 완료 → PASS: {pass_cnt}, FAIL: {fail_cnt}, SKIP: {skip_cnt} (총 {len(report['tests'])}개)")

                for test in report["tests"]:
                    outcome = test.get("outcome")
                    call_info = test.get("call", {})

                    # ✅ 함수 단위 duration 가져오기
                    func_duration = call_info.get("duration", 0.0)

                    save_test_result(
                        test_name=test.get("nodeid", "").split("::")[-1],
                        message="테스트 성공" if outcome == "passed" else outcome,
                        status="PASS" if outcome == "passed"
                            else "FAIL" if outcome == "failed"
                            else "SKIP",
                        file_name=test_file,
                        stack_trace="\n".join(call_info.get("longrepr", "").splitlines()[-5:])
                                    if outcome == "failed" else "",
                        duration=f"{func_duration:.2f}초"
                    )
            else:
                # report.json은 있는데 tests 항목이 없음 → pytest 실행 오류
                save_test_result(
                    test_name=os.path.splitext(os.path.basename(test_file))[0],
                    message="pytest 실행 오류",
                    status="FAIL",
                    file_name=test_file,
                    stack_trace=e.stderr if 'e' in locals() else "",
                    duration=f"{duration:.2f}초"
                )
        else:
            # result.json 자체가 없는 경우
            save_test_result(
                test_name=os.path.splitext(os.path.basename(test_file))[0],
                message="pytest 실행 오류 (결과 파일 없음)",
                status="FAIL",
                file_name=test_file,
                stack_trace=e.stderr if 'e' in locals() else "",
                duration=f"{duration:.2f}초"
            )

print("\n🎯 모든 테스트 완료")

print("\n📤 슬랙 메시지 전송 중...")
subprocess.run(["python", "scripts/send_slack.py"])
