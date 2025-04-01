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
    # 한국 시간 기준
    seoul_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")
    summary_path = os.path.join("scripts", "summary.json")

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_tests = data.get("tests", [])
    except FileNotFoundError:
        send_slack_message(f"❗ [{seoul_time}] summary.json 파일이 없습니다.")
        return
    except json.JSONDecodeError as e:
        send_slack_message(f"❗ [{seoul_time}] summary.json 파싱 오류: {e}")
        return

    if not all_tests:
        send_slack_message(f"⚠️ [{seoul_time}] 테스트가 실행되지 않았습니다. summary.json의 테스트 항목이 비어 있습니다.")
        return

    passed_tests = [t for t in all_tests if t.get("status") == "passed"]
    failed_tests = [t for t in all_tests if t.get("status") == "failed"]

    message = f"📢 [{seoul_time}] 테스트 결과 요약\n"
    message += f"총 테스트 수: {len(all_tests)}개\n"

    if passed_tests:
        message += "\n🟩 성공 테스트 목록:\n"
        for i, test in enumerate(passed_tests, 1):
            message += f"{i}. {test.get('name', '이름 없음')}\n"

    if failed_tests:
        message += "\n🟥 실패 테스트 목록:\n"
        for i, test in enumerate(failed_tests, 1):
            line = f"{i}. {test.get('name', '이름 없음')}"
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
