import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_BASE_URL = os.getenv("JIRA_URL")

now = datetime.utcnow() + timedelta(hours=9)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 테스트 이름 → 한글 이름 매핑
TEST_NAME_MAPPING = {
    "test_delete_category_each": "카테고리 삭제 확인",
    "test_edit_category_each": "카테고리 수정 확인",
    "test_register_category_each": "카테고리 등록 확인",
    "test_delete_product": "제품 삭제 확인",
    "test_bulk_delete_products": "제품 일괄 삭제 확인",
    "test_edit_single_product": "단일 제품 수정 확인",
    "test_edit_bulk_products": "제품 일괄 수정 확인",
    "test_register_product": "제품 등록 확인",
    "test_stock_inflow": "재고 입고 확인",
    "test_stock_outflow": "재고 출고 확인",
    "test_Bay_stock_out": "재고 출고 전체 테스트",
    "test_Bay_prdctg_delete": "카테고리 삭제 테스트",
    "delete_product_and_verify": "제품 삭제 검증",
    "test_Bay_product_delete": "제품 삭제 테스트",
    "test_Bay_order_status_request_cancel": "발주 취소 테스트",
    "test_Bay_order_status_request": "발주 요청 테스트",
    "test_Bay_order_status_progress_delivery": "배송 진행 테스트",
    "test_Bay_order_status_progress_complete": "수령 완료 테스트",
    "test_Bay_order_status_delivery": "배송 상태 확인",
    "test_Bay_order_status_complete": "발주 완료 테스트",
    "test_Bay_order_status_fail": "발주 실패 상태 확인",
}

def get_korean_name(test_name):
    return TEST_NAME_MAPPING.get(test_name, test_name)

def load_existing_issues():
    path = "existing_issues.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def send_slack_message(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"❌ Slack 전송 실패: {response.status_code} - {response.text}")
    else:
        print("✅ Slack 메시지 전송 완료")

def main():
    results_path = "test_results.json"
    existing_issues = load_existing_issues()

    try:
        with open(results_path, "r", encoding="utf-8") as f:
            all_tests = json.load(f)
    except FileNotFoundError:
        send_slack_message(f"❗ [{seoul_time}] test_results.json 파일이 없습니다.")
        return

    passed = [t for t in all_tests if t["status"] == "PASS"]
    failed = [t for t in all_tests if t["status"] == "FAIL"]
    skipped = [t for t in all_tests if t["status"] == "SKIP"]

    lines = [f"\n📦 *자동화 테스트 결과* ({seoul_time})"]
    lines.append(f"✅ 성공: {len(passed)} | ❌ 실패: {len(failed)} | ⏭️ 스킵: {len(skipped)}")

    if failed:
        lines.append("\n❗ *실패 테스트 목록:*")
        for i, test in enumerate(failed, start=1):
            name = get_korean_name(test["test_name"])
            issue_key = existing_issues.get(test["test_name"])
            if issue_key:
                jira_url = f"{JIRA_BASE_URL}/browse/{issue_key}"
                lines.append(f"{i}. {name} — 🔗 <{jira_url}|{issue_key}>")
            else:
                lines.append(f"{i}. {name} —  ❌ {test['message'].splitlines()[0]}")

    if skipped:
        lines.append("\n⚠️ *스킵된 테스트 목록:*")
        for i, test in enumerate(skipped, start=1):
            name = get_korean_name(test["test_name"])
            lines.append(f"{i}. {name} — {test['message']}")

    send_slack_message("\n".join(lines))

if __name__ == "__main__":
    main()
