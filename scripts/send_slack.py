import json
import os
import requests
from datetime import datetime


SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
# JIRA_URL = os.getenv("JIRA_URL")

def send_slack_message(text):
    payload = { "text": text }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Slack 전송 실패:", response.text)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        with open("summary.json", "r", encoding="utf-8") as f:
            all_tests = json.load(f)
    except FileNotFoundError:
        send_slack_message(f"⚠️ [{now}] summary.json 파일이 존재하지 않습니다.")
        return

    passed_tests = [t for t in all_tests if t["status"] == "passed"]
    failed_tests = [t for t in all_tests if t["status"] == "failed"]

    message = f"📢 [{now}] 테스트 결과 \n"

    # 성공 테스트 목록
    if passed_tests:
        message += f"\n🟦 성공 테스트 목록:\n"
        for i, test in enumerate(passed_tests, 1):
            message += f"{i}. {test['name']}\n"

    # 실패 테스트 목록
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


response = requests.post(SLACK_WEBHOOK_URL, json={"text": test_message})
print("전송 결과", response.status_code)