import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
RESULT_FILE = "test_results.json"

# 시간 포맷 (KST)
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 버전 정보 불러오기
def load_version():
    base_path = os.path.dirname(os.path.abspath(__file__))
    version_path = os.path.join(base_path, "..", "tests", "version_info.json")

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "버전 정보 없음")
    except FileNotFoundError:
        return "버전 정보 없음"

# 테스트 파일명 → 한글 매핑
test_file_to_korean = {
    "test_Bay_login": "로그인 확인",
    "test_Bay_alert" : "공통 토스트 팝업 및 검색 기능 확인",
    "test_Bay_order_status_request_cancel": "발주 취소 상태 확인",
    "test_Bay_order_status_request": "발주 요청 상태 확인",
    "test_Bay_order_status_progress_delivery": "발주 진행 상태에서 운송장 등록 확인",
    "test_Bay_order_status_progress_complete": "발주 진행 상태에서 수령 확인",
    "test_Bay_order_status_delivery": "배송 진행 상태 확인",
    "test_Bay_order_status_complete": "수령 완료 상태 확인",
    "test_Bay_order_status_fail": "발주 실패 상태 확인",
    "test_Bay_product_delete": "제품 삭제 확인",
    "test_Bay_product_edit": "제품 수정 확인",
    "test_Bay_product_val": "제품 등록 유효성 검사",
    "test_Bay_product": "제품 등록 확인",
    "test_Bay_prdctg_delete": "카테고리 삭제 확인",
    "test_Bay_prdctg_val": "카테고리 등록 유효성 검사",
    "test_Bay_prdctg_edit": "카테고리 수정 확인",
    "test_Bay_prdctg": "카테고리 등록 확인",
    "test_Bay_supplier": "업체 등록 확인",
    "test_Bay_supplier_val": "업체 등록 유효성 검사",
    "test_Bay_supplier_delete": "업체 삭제 확인",
    "test_Bay_stock_in": "재고 입고 확인",
    "test_Bay_stock_out": "재고 출고 확인",
    "test_Bay_stock_history":"재고 상세 내역 확인",
    "test_Bay_order_status_batch":"규칙 발주 내역 확인",
    "test_Bay_stock_batch":"여러 제품 규칙 발주 확인",
    "test_Bay_rules_register":"발주 규칙 등록 확인",
    "test_Bay_rules_edit":"발주 규칙 수정 확인",
}

def load_test_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_duration(total_seconds):
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}분 {seconds}초"

def get_total_duration_from_results(results):
    total = 0.0
    for r in results:
        try:
            duration = float(r.get("duration", "0").replace("초", ""))
            total += duration
        except:
            continue
    return format_duration(total)

def build_slack_message(test_results):
    version = load_version()
    success_count = 0
    fail_count = 0
    skip_count = 0
    detail_lines = []

    for idx, result in enumerate(test_results, 1):
        test_name = result.get("test_name")
        status = result.get("status")
        message = result.get("message", "")

        korean_name = test_file_to_korean.get(test_name, test_name)

        if status == "PASS":
            success_count += 1
            detail_lines.append(f"{idx}. ✅[PASS] {korean_name}")
        elif status == "FAIL":
            fail_count += 1
            detail_lines.append(f"{idx}. ❌[FAIL] {korean_name}\n   {message}")
        elif status == "SKIP":
            skip_count += 1
            detail_lines.append(f"{idx}. [SKIP] {korean_name}")

    total_time = get_total_duration_from_results(test_results)

    slack_message = f":mega: *[CenturionBay] 자동화 테스트 결과* ({seoul_time})\n"
    slack_message += f"버전: :centurionlogo: `{version}`\n"
    slack_message += f"Total: {len(test_results)} | ✅PASS: {success_count} | FAIL: ❌{fail_count} \n"
    slack_message += f":stopwatch: 전체 수행 시간: {total_time}\n\n"
    slack_message += "\n".join(detail_lines)

    return slack_message

def send_slack_message(message):
    payload = {
        "text": message
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message to Slack: {response.status_code}, {response.text}")

if __name__ == "__main__":
    test_results = load_test_results(RESULT_FILE)
    slack_message = build_slack_message(test_results)
    send_slack_message(slack_message)
    print("✅ 슬랙 알림이 전송되었습니다.")
