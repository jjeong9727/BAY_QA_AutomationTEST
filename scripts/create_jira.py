
import json
import os
import requests
from requests.auth import HTTPBasicAuth

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = "QA"

def create_issue(summary, description):
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": { "key": PROJECT_KEY },
            "summary": summary,
            "description": description,
            "issuetype": { "name": "Bug" }
        }
    }
    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 201:
        return response.json()["key"]
    else:
        print("Jira 등록 실패:", response.text)
        return None

def main():
    try:
        with open("failures.json", "r", encoding="utf-8") as f:
            failures = json.load(f)
    except FileNotFoundError:
        print("failures.json 파일이 존재하지 않습니다.")
        return

    for fail in failures:
        summary = f"[TEST FAIL] {fail['name']}"
        description = f"*파일:* {fail['file']}\n\n*에러 메시지:*\n{fail['message']}\n\n*스택 트레이스:*\n{fail['stack']}"
        issue_key = create_issue(summary, description)
        if issue_key:
            fail["jira_key"] = issue_key

    with open("failures.json", "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
