import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_BASE_URL = os.getenv("JIRA_URL")

# 한국 시간 기준 타임스탬프
now = datetime.utcnow() + timedelta(hours=9)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 기존 등록된 Jira 이슈 정보 로드
def load_existing_issues():
    path = "existing_issues.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 슬랙 메시지 전송 함수
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
    except json.JSONDecodeError as e:
        send_slack_message(f"❗ [{seoul_time}] test_results.json 파싱 오류: {e}")
        return

    passed_tests = [t for t in all_tests if t.get("status") == "PASS"]
    failed_tests = [t for t in all_tests if t.get("status") == "FAIL"]
    skipped_tests = [t for t in all_tests if t.get("status") == "SKIP"]

    message_lines = [f"\n📦 *자동화 테스트 결과* ({seoul_time})"]
    message_lines.append(f"✅ 성공: {len(passed_tests)} | ❌ 실패: {len(failed_tests)} | ⏭️ 스킵: {len(skipped_tests)}")

    if failed_tests:
        message_lines.append("\n*❗ 실패 테스트 목록:*")
        for test in failed_tests:
            test_key = test['test_name']
            issue_key = existing_issues.get(test_key)
            if issue_key:
                jira_url = f"{JIRA_BASE_URL}/browse/{issue_key}"
                message_lines.append(f"• {test_key} — 이미 등록된 이슈: <{jira_url}|{issue_key}>")
            else:
                message_lines.append(f"• {test_key} — {test['message']}")

    if skipped_tests:
        message_lines.append("\n*⚠️ 스킵된 테스트 목록:*")
        for test in skipped_tests:
            message_lines.append(f"• {test['test_name']} — {test['message']}")

    send_slack_message("\n".join(message_lines))

if __name__ == "__main__":
    main()
