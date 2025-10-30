import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "BAY")

def search_resolved_issues():
    """
    RESOLVED 상태의 automation 이슈만 검색

    JQL: project = BAY AND labels = "automation" AND status = "RESOLVED"
    """
    jql = f'project = {PROJECT_KEY} AND labels = "automation" AND status = "RESOLVED"'

    url = f"{JIRA_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "fields": "key,status,summary,labels"
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json().get("issues", [])
        else:
            print(f"⚠️ Jira 검색 실패: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"❌ Jira 검색 오류: {e}")
        return []

def extract_screen_label(issue):
    """
    이슈의 Label에서 화면명 추출

    Labels: ["automation", "login"] → "login"
    """
    labels = issue.get("fields", {}).get("labels", [])

    # automation을 제외한 나머지 label 추출
    screen_labels = [l for l in labels if l != "automation"]

    if screen_labels:
        return screen_labels[0]  # 첫 번째 화면 label 반환
    return None

def check_test_results_for_label(label, test_results):
    """
    특정 Label의 테스트 결과 확인

    Returns:
        str: "PASS", "FAIL", "NOT_FOUND"
    """
    # test_Bay_{label}.py 패턴으로 파일명 매칭
    target_file = f"test_Bay_{label}.py"

    found_tests = []
    for result in test_results:
        file_name = result.get("file", "")
        if target_file in file_name:
            found_tests.append(result)

    if not found_tests:
        return "NOT_FOUND"

    # 하나라도 FAIL이면 FAIL
    for test in found_tests:
        if test.get("status") == "FAIL":
            return "FAIL"

    # 모두 PASS
    return "PASS"

def close_issue(issue_key):
    """
    이슈를 CLOSED 상태로 전환
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"

    try:
        # 1. 가능한 transition 조회
        response = requests.get(
            url,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            print(f"  ⚠️ Transition 조회 실패: {issue_key}")
            return False

        transitions = response.json().get("transitions", [])

        # 2. "Close" or "Done" transition 찾기
        close_transition = None
        for t in transitions:
            name_lower = t.get("name", "").lower()
            if "close" in name_lower or "done" in name_lower:
                close_transition = t.get("id")
                break

        if not close_transition:
            print(f"  ⚠️ Close transition을 찾을 수 없음: {issue_key}")
            return False

        # 3. Close 실행
        payload = {"transition": {"id": close_transition}}
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            print(f"  ✅ Close 완료: {issue_key}")
            return True
        else:
            print(f"  ⚠️ Close 실패: {response.status_code}, {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Close 오류: {e}")
        return False

def add_comment_to_issue(issue_key, comment):
    """기존 이슈에 코멘트 추가"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }
            ]
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            return True
        else:
            print(f"  ⚠️ 코멘트 추가 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 코멘트 추가 오류: {e}")
        return False

def verify_resolved_issues(test_results_path="test_results.json"):
    """
    RESOLVED 상태 이슈 검증

    로직:
    1. RESOLVED 이슈 조회
    2. 각 이슈의 Label로 테스트 결과 확인
    3. PASS → Close
    4. FAIL → 이미 Reopen 되었을 것 (스킵)
    5. NOT_FOUND → 경고
    """
    print("=" * 60)
    print("🔍 Jira RESOLVED 이슈 검증 시작")
    print("=" * 60)

    # 1. 테스트 결과 로드
    if not os.path.exists(test_results_path):
        print(f"❌ 테스트 결과 파일 없음: {test_results_path}")
        return []

    with open(test_results_path, "r", encoding="utf-8") as f:
        test_results = json.load(f)

    # 2. RESOLVED 이슈 조회
    resolved_issues = search_resolved_issues()

    if not resolved_issues:
        print("\n✅ RESOLVED 상태 이슈가 없습니다.")
        return []

    print(f"\n📋 검증할 RESOLVED 이슈: {len(resolved_issues)}개\n")

    verification_results = []

    # 3. 각 이슈 검증
    for issue in resolved_issues:
        issue_key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")

        print(f"🔍 검증 중: {issue_key} - {summary}")

        # Label 추출
        label = extract_screen_label(issue)

        if not label:
            print(f"  ⚠️ 화면 Label 없음 → 수동 확인 필요")
            verification_results.append({
                "key": issue_key,
                "action": "no_label",
                "result": "SKIP"
            })
            continue

        print(f"  📌 Label: {label}")

        # 테스트 결과 확인
        test_result = check_test_results_for_label(label, test_results)

        if test_result == "NOT_FOUND":
            print(f"  ⚠️ 테스트 결과 없음 → 수동 확인 필요")
            comment = "⚠️ 자동 검증 불가: 해당 테스트 결과를 찾을 수 없습니다."
            add_comment_to_issue(issue_key, comment)

            verification_results.append({
                "key": issue_key,
                "label": label,
                "action": "not_found",
                "result": "SKIP"
            })

        elif test_result == "FAIL":
            print(f"  ⚠️ 테스트 FAIL → 이미 Reopen 되었을 것 (스킵)")
            verification_results.append({
                "key": issue_key,
                "label": label,
                "action": "already_reopened",
                "result": "SKIP"
            })

        elif test_result == "PASS":
            print(f"  ✅ 테스트 PASS → Close 처리")
            comment = "✅ 자동 검증 완료: 모든 테스트 통과"
            add_comment_to_issue(issue_key, comment)

            # Close 처리 전 상태 저장
            previous_status = "RESOLVED"
            close_success = close_issue(issue_key)
            new_status = "CLOSED" if close_success else "RESOLVED"

            verification_results.append({
                "key": issue_key,
                "label": label,
                "summary": summary,
                "action": "closed",
                "result": "SUCCESS",
                "previous_status": previous_status,
                "new_status": new_status
            })

    # 4. 결과 저장
    output_path = "resolved_issues_verification.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(verification_results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 검증 완료")
    print(f"📁 저장 위치: {output_path}")

    return verification_results

if __name__ == "__main__":
    try:
        results = verify_resolved_issues()

        # 요약 출력
        print("\n" + "=" * 60)
        print("📊 검증 결과 요약")
        print("=" * 60)

        closed = [r for r in results if r.get("action") == "closed"]
        skipped = [r for r in results if r.get("result") == "SKIP"]

        print(f"  ✅ Close 처리: {len(closed)}개")
        print(f"  ⏭️ 스킵: {len(skipped)}개")
        print(f"  📝 총 검증: {len(results)}개")

        if closed:
            print("\n✅ Close 처리된 이슈:")
            for r in closed:
                print(f"  - {r.get('key')} (Label: {r.get('label')})")

    except Exception as e:
        print(f"\n❌ 실행 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()
