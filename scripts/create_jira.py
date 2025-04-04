import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests

load_dotenv()

# 환경 변수
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

ISSUE_STORAGE_FILE = "existing_issues.json"

# 기존 이슈들을 외부 파일로 저장하고 불러오기
def load_existing_issues():
    if os.path.exists(ISSUE_STORAGE_FILE):
        with open(ISSUE_STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_existing_issues(existing_issues):
    with open(ISSUE_STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_issues, file, indent=2, ensure_ascii=False)
    print("💾 existing_issues.json에 데이터 저장 완료")

# Jira 이슈 생성 함수
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
                            {"type": "text", "text": description}
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

# 배치 초기화 함수: 새로운 배치가 시작될 때마다 초기화
def reset_batch_files():
    # result.json 및 summary.json 초기화
    if os.path.exists("scripts/result.json"):
        os.remove("scripts/result.json")
        print("✅ result.json 파일 초기화 완료")

    if os.path.exists("scripts/summary.json"):
        os.remove("scripts/summary.json")
        print("✅ summary.json 파일 초기화 완료")

def main():
    reset_batch_files()  # 새로운 배치가 시작되면 파일 초기화

    summary_path = os.path.join("scripts", "summary.json")

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❗ summary.json 파일이 없거나 파싱에 실패했습니다.")
        return

    if not data:
        print("⚠️ summary.json에 테스트 결과가 없습니다. Jira 등록을 건너뜁니다.")
        return

    # 기존 이슈 로드
    existing_issues = load_existing_issues()
    changed = False
    for t in data:  # data가 리스트 형태일 경우
        if t.get("status") == "failed" and "jira_key" not in t:
            test_name = t.get("name", "테스트 실패").strip()
            print(f"[LOG] 현재 테스트 이름: {test_name}")

            # 새로운 이슈를 생성
            summary = test_name
            description = (
                f"*파일:* {t.get('file', '알 수 없음')}\n\n"
                f"*에러 메시지:*\n{t.get('message', '없음')}\n\n"
                f"*스택 트레이스:*\n{t.get('stack', '없음')}"
            )
            issue_key = create_issue(summary, description)
            if issue_key:
                t["jira_key"] = issue_key  # 새로운 이슈의 jira_key 저장
                existing_issues[test_name] = issue_key  # 새로운 이슈 정보 저장
                save_existing_issues(existing_issues)  # 저장
                changed = True

    if changed:
        # 변경된 이슈 정보 저장
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("💾 summary.json에 Jira 키 저장 완료")

if __name__ == "__main__":
    main()
