import json
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9 이상에서 지원
from dotenv import load_dotenv
load_dotenv()

# 환경 변수에서 Slack Webhook과 Jira URL 가져오기
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_URL = os.getenv("JIRA_URL")

def send_slack_message(text):
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
    if response.status_code != 200:
        print("Slack 전송 실패:", response.text)

def main():
    # 한국 시간으로 현재 시각
    now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")
    summary_path = os.path.join("scripts", "summary.json")

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_tests = data.get("tests", [])
    except (FileNotFoundError, json.JSONDecodeError):
        send_slack_message(f"❗ [{now}] summary.json 파일이 없거나 파싱에 실패했습니다.")
        return

    total_tests = len(all_tests)
    passed_tests = [t for t in all_tests if t["status"] == "passed"]
    failed_tests = [t for t in all_tests if t["status"] == "failed"]

    if total_tests == 0:
        send_slack_message(f"⚠️ [{now}] 테스트가 실행되지 않았습니다. summary.json에 테스트 결과가 없습니다.")
        return

    message = f"📢 [{now}] 테스트 결과 요약\n"
    message += f"총 테스트 수: {total_tests}개\n"

    if passed_tests:
        message += f"\n🟩 성공 테스트 목록:\n"
        for i, test in enumerate(passed_tests, 1):
            message += f"{i}. {test['name']}\n"

    if failed_tests:
        message += f"\n🟥 실패 테스트 목록:\n"
        for i, test in enumerate(failed_tests, 1):
            line = f"{i}. {test['name']}"
            if "jira_key" in test:
                line += f"\n   → {JIRA_URL}/browse/{test['jira_key']}"
            else:
                line += "\n   → Jira 등록 실패"
            message += line + "\n"
    else:
        message += "\n🎉 모든 테스트가 통과했습니다!"

    send_slack_message(message)

if __name__ == "__main__":
    main()
