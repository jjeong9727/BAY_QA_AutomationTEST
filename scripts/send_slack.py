import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_BASE_URL = os.getenv("JIRA_URL")
RESULT_FILE = "test_results.json"
EXISTING_ISSUES_FILE = "existing_issues.json"

KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 테스트 이름 → 한글 이름 매핑
TEST_NAME_MAPPING = {
    "test_login_success": "로그인 성공",
    "test_login_wrong_password": "로그인 비밀번호 오류",
    "test_order_status_cancel": "발주 취소 상태 확인",
    "test_order_status_complete": "발주 완료 상태 확인",
    "test_order_receive_from_delivery": "배송 상태에서 수령 확인",
    "test_order_status_fail": "발주 실패 상태 확인",
    "test_order_receive_from_progress": "진행 중 상태에서 수령 확인",
    "test_order_delivery": "배송 상태 확인",
    "test_order_cancel": "발주 취소 상태 확인",
    "test_order_acceptance": "발주 수락 확인",
    "test_delete_category_each": "카테고리 삭제 확인",
    "test_edit_category_each": "카테고리 수정 확인",
    "test_duplicate_category_names": "카테고리 중복 등록 확인",
    "test_register_category_each": "카테고리 등록 확인",
    "test_delete_product_validation": "제품 삭제 유효성 검사",
    "test_delete_product": "제품 삭제 확인",
    "test_bulk_delete_products": "제품 일괄 삭제 확인",
    "test_edit_single_product": "단일 제품 수정 확인",
    "test_edit_bulk_products": "제품 일괄 수정 확인",
    "test_duplicate_product_name": "제품명 중복 확인",
    "test_register_product": "제품 등록 확인",
    "test_register_multiple_products": "제품 일괄 등록 확인",
    "test_stock_inflow": "재고 입고 확인",
    "test_stock_outflow": "재고 출고 확인",
    "test_delete_supplier": "업체 삭제 확인",
    "test_register_supplier_duplicate": "업체 중복 확인",
    "test_register_supplier": "업체 등록 확인"
}

def get_korean_name(test_name):
    return TEST_NAME_MAPPING.get(test_name, test_name)

def load_existing_issues():
    if os.path.exists(EXISTING_ISSUES_FILE):
        with open(EXISTING_ISSUES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

EMOJI_PASS = "✅"
EMOJI_FAIL = "🟥"
EMOJI_SKIP = "⏭️"
EMOJI_ARROW = "➡️"

def build_slack_message():
    if not os.path.exists(RESULT_FILE):
        return f"❗ test_results.json 파일이 존재하지 않습니다."

    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)

    existing_issues = load_existing_issues()

    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]
    skipped = [r for r in results if r["status"] == "SKIP"]
    total = len(results)

    lines = [f":package: *자동화 테스트 결과* ({seoul_time})"]
    lines.append(f"*총 수행 테스트 수: {total}*")
    lines.append(f"🟩 성공: {len(passed)} | {EMOJI_FAIL} 실패: {len(failed)} |  스킵: {len(skipped)}")
    

    if failed:
        lines.append(f"\n{EMOJI_FAIL} *실패 테스트 목록:*")
        for idx, r in enumerate(failed, 1):
            name = get_korean_name(r["test_name"])
            issue_key = existing_issues.get(r["test_name"])
            if issue_key:
                link = f"{JIRA_BASE_URL}/browse/{issue_key}"
                lines.append(f"{idx}. {name} \n — 이미 등록된 이슈: <{link}|{issue_key}>")
            else:
                msg = r["message"].strip().split("\n")[0]  # 첫 줄만 추출
                lines.append(f"{idx}. {name} {EMOJI_FAIL}\n{EMOJI_ARROW} {msg}")

    if skipped:
        lines.append(f"\n🟨 *스킵된 테스트 목록:*")
        for idx, r in enumerate(skipped, 1):
            name = get_korean_name(r["test_name"])
            msg = r.get("message", "")
            lines.append(f"{idx}. {name} — {msg}")

    if passed:
        lines.append(f"\n🟩 *통과한 테스트 목록:*")
        for idx, r in enumerate(passed, 1):
            name = get_korean_name(r["test_name"])
            lines.append(f"{idx}. {name}")

    return "\n".join(lines)

def send_slack_message(text):
    payload = {"text": text}
    res = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if res.status_code == 200:
        print("✅ Slack 전송 성공")
    else:
        print(f"❌ Slack 전송 실패: {res.status_code}\n{res.text}")

if __name__ == "__main__":
    msg = build_slack_message()
    print(msg)
    send_slack_message(msg)
