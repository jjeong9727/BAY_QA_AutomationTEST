import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# .env 파일에서 값 불러오기
load_dotenv()

# Jira 설정 값 불러오기

jira_url = os.getenv('JIRA_URL')
jira_email = os.getenv('JIRA_EMAIL')
assignee_email = os.getenv('ASSIGNEE_EMAIL')
api_token = os.getenv('JIRA_API_TOKEN')
issue_key = os.getenv('ISSUE_KEY')
# assignee_username = os.getenv('ASSIGNEE_USERNAME')
file_path = os.getenv('SCREENSHOT_PATH')
status_id = os.getenv('STATUS_ID')

# 이슈 업데이트 함수들
def get_account_id(email):
    url = f"{jira_url}/rest/api/3/user/search?query={email}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(jira_email, api_token),
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        users = response.json()
        if users:
            return users[0].get("accountId")
        else:
            print("❌ 사용자 정보를 찾을 수 없습니다.")
            return None
    else:
        print(f"❌ Jira 사용자 조회 실패: {response.status_code}, {response.text}")
        return None

# 담당자 지정 함수
def assign_issue(issue_key, assignee_email):
    # 이메일로 accountId 가져오기
    assignee_account_id = get_account_id(assignee_email)
    if not assignee_account_id:
        return  # accountId가 없으면 더 이상 진행하지 않음

    url = f"{jira_url}/rest/api/3/issue/{issue_key}/assignee"
    payload = {
        "accountId": assignee_account_id
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 사용자 지정 요청
        response = requests.put(
            url,
            json=payload,
            auth=HTTPBasicAuth(jira_email, api_token),
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"✅ 담당자 지정 완료: {issue_key} -> {assignee_email}")
        else:
            print(f"❌ 담당자 지정 실패: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def attach_file_to_jira(issue_key, file_path):
    """Jira 이슈에 스크린샷 또는 첨부파일을 추가하는 함수"""
    url = f"{jira_url}/rest/api/3/issue/{issue_key}/attachments"
    headers = {
        "X-Atlassian-Token": "no-check"  # 필수 헤더 (Jira API 요구 사항)
    }

    # 파일 열기 및 Jira API로 파일 첨부 요청
    with open(file_path, 'rb') as file:
        response = requests.post(url, headers=headers, files={'file': file}, auth=HTTPBasicAuth(jira_email, api_token))
        
    if response.status_code == 200:
        print(f"파일이 Jira 이슈 {issue_key}에 첨부되었습니다.")
    else:
        print(f"파일 첨부 실패: {response.status_code}, {response.text}")


def change_status(issue_key, status_id):
    url = f"{jira_url}/rest/api/3/issue/{issue_key}/transitions"
    payload = {
        "transition": {
            "id": status_id
        }
    }
    response = requests.post(url, json=payload, auth=HTTPBasicAuth(username, api_token))
    if response.status_code == 204:
        print(f"상태 변경 완료: {status_id}")
    else:
        print(f"상태 변경 실패: {response.status_code}")

# 각 작업 실행
assign_issue(issue_key, assignee_email)
attach_file_to_jira(issue_key, file_path)
# change_status(issue_key, status_id)

