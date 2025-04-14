import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

EXISTING_ISSUES_PATH = "existing_issues.json"

def load_existing_issues():
    if os.path.exists(EXISTING_ISSUES_PATH):
        with open(EXISTING_ISSUES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_existing_issues(issues_dict):
    with open(EXISTING_ISSUES_PATH, "w", encoding="utf-8") as f:
        json.dump(issues_dict, f, indent=2, ensure_ascii=False)

def create_issue(summary, description):
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
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
            "issuetype": {"name": "Bug"}
        }
    }

    response = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Content-Type": "application/json"}
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

def register_failed_issues_from_summary(summary_path="scripts/summary.json"):
    with open(summary_path, "r", encoding="utf-8") as f:
        test_results = json.load(f)

    existing_issues = load_existing_issues()

    for test in test_results:
        if test.get("status", "").lower() != "fail":
            continue

        test_key = test.get("name", "").strip()  # 전체 name 값 사용

        if test_key in existing_issues:
            print(f"⏭️ 이미 등록된 이슈: {test_key} → {existing_issues[test_key]}")
            continue

        summary = test.get("name")
        message = test.get("message", "")
        stack = test.get("stack", "")
        description = f"{message}\n\n{stack}"

        issue_key = create_issue(summary, description)

        if issue_key:
            existing_issues[test_key] = issue_key
            save_existing_issues(existing_issues)


if __name__ == "__main__":
    print("📌 Jira 이슈 자동 등록 시작")
    try:
        register_failed_issues_from_summary()
    except Exception as e:
        print(f"❌ 실행 중 예외 발생: {e}")
