import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
ASSIGNEE = os.getenv("JIRA_ASSIGNEE")  # 담당자 이메일

def create_issue(summary, description):
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Bug"},
            "assignee": {"name": ASSIGNEE}  # 담당자 지정
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

def add_attachment_to_issue(issue_key, file_path):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments"
    headers = {
        "X-Atlassian-Token": "no-check",
    }
    files = {
        'file': open(file_path, 'rb'),
    }
    response = requests.post(
        url,
        headers=headers,
        files=files,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    if response.status_code == 200:
        print("✅ 스크린샷 첨부 완료")
    else:
        print("❌ 스크린샷 첨부 실패")
        print("Status:", response.status_code)
        print("Body:", response.text)
