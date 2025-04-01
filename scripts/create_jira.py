import json
import os
import requests
from requests.auth import HTTPBasicAuth

# 환경 변수
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECTKEY")

def create_issue(summary, description):
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": { "key": PROJECT_KEY },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": { "name": "Bug" }
        }
    }

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={ "Content-Type": "application/json" }
    )
    if response.status_code == 201:
        issue_key = response.json().get("key")
        print(f"✅ Jira 이슈 생성 완료: {issue_key}")
        return issue_key
    else:
        print("❌ Jira 등록 실패:")
        print("Status:", response.status_code)
        print("Body:", response.text)
        return None

def main():
    summary_path = os.path.join("scripts", "summary.json")

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            tests = data.get("tests", [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("❗ summary.json 파일이 없거나 파싱에 실패했습니다.")
        return

    if not tests:
        print("⚠️ summary.json에 테스트 결과가 없습니다. Jira 등록을 건너뜁니다.")
        return

    changed = False
    for t in tests:
        if t.get("status") == "failed" and "jira_key" not in t:
            summary = t.get("name", "테스트 실패")
            description = (
                f"*파일:* {t.get('file', '알 수 없음')}\n\n"
                f"*에러 메시지:*\n{t.get('message', '없음')}\n\n"
                f"*스택 트레이스:*\n{t.get('stack', '없음')}"
            )
            issue_key = create_issue(summary, description)
            if issue_key:
                t["jira_key"] = issue_key
                changed = True

    if changed:
        data["tests"] = tests  # 수정된 테스트 정보 저장
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("💾 summary.json에 Jira 키 저장 완료")

if __name__ == "__main__":
    main()
