import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.test_name_mapping import test_name_mapping   # ✅ 공통 매핑 불러오기

# 환경 변수 로드
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
JIRA_URL = os.getenv("JIRA_URL", "https://medisolveai.atlassian.net")
RESULT_FILE = "test_results.json"
JIRA_ISSUES_FILE = "jira_created_issues.json"
CONFLUENCE_URL_FILE = "confluence_report_url.txt"
VERIFICATION_FILE = "resolved_issues_verification.json"

# 시간 포맷 (KST)
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 버전 정보 불러오기
def load_version():
    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_path, ".."))
    version_path = os.path.join(project_root, "tests", "version_info.json")

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            version = data.get("version", "버전 정보 없음")
            print(f"✅ 불러온 버전: {version}")
            return version
    except FileNotFoundError:
        print(f"⚠️ version_info.json 파일을 찾을 수 없음: {version_path}")
        return "버전 정보 없음"
    except json.JSONDecodeError:
        print(f"⚠️ version_info.json 파싱 실패: {version_path}")
        return "버전 정보 없음"

def load_test_results(file_path):
    """테스트 결과 로드"""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jira_issues():
    """Jira 이슈 목록 로드"""
    if not os.path.exists(JIRA_ISSUES_FILE):
        return []
    with open(JIRA_ISSUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_confluence_url():
    """Confluence 리포트 URL 로드"""
    if not os.path.exists(CONFLUENCE_URL_FILE):
        return None
    with open(CONFLUENCE_URL_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_verification_results():
    """검증 결과 로드"""
    if not os.path.exists(VERIFICATION_FILE):
        return []
    with open(VERIFICATION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_duration(total_seconds):
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}분 {seconds}초"

def get_total_duration_from_results(results):
    total = 0.0
    for r in results:
        try:
            duration = float(r.get("duration", "0").replace("초", ""))
            total += duration
        except:
            continue
    return format_duration(total)

def build_slack_message(test_results, jira_issues, confluence_url, verification_results):
    """
    슬랙 메시지 구성

    포함 내용:
    1. 테스트 결과 통계
    2. Jira 이슈 링크
    3. Confluence 리포트 URL
    4. 검증 결과 (상태 변경된 이슈)
    5. 파일별 상세 결과
    """
    version = load_version()
    success_count = 0
    fail_count = 0
    skip_count = 0
    grouped_results = {}

    # 파일 단위로 그룹핑
    for result in test_results:
        file_name = os.path.basename(result.get("file", ""))
        test_func = result.get("test_name", "")
        status = result.get("status", "")

        # ✅ 매핑 적용 (없으면 원래 값 사용)
        file_display = test_name_mapping.get(file_name, file_name)
        func_display = test_name_mapping.get(test_func, test_func)

        if status == "PASS":
            success_count += 1
        elif status == "FAIL":
            fail_count += 1
        elif status == "SKIP":
            skip_count += 1

        grouped_results.setdefault(file_display, []).append((func_display, status))

    total_time = get_total_duration_from_results(test_results)

    # ============================================================
    # 헤더 부분
    # ============================================================
    slack_message = f":mega: *[CenturionBay] 자동화 테스트 결과* ({seoul_time})\n"
    slack_message += f"버전: :centurionlogo: `{version}`\n"
    slack_message += f"Total: {len(test_results)} | ✅ PASS: {success_count} | ❌ FAIL: {fail_count} | ⚪ SKIP: {skip_count}\n"
    slack_message += f":stopwatch: 전체 수행 시간: {total_time}\n\n"

    # ============================================================
    # Jira 이슈 목록
    # ============================================================
    if jira_issues:
        slack_message += "*🐞 Jira 이슈*\n"

        created_issues = [i for i in jira_issues if i.get("action") == "created"]
        existing_issues = [i for i in jira_issues if i.get("action") == "existing_open"]
        reopened_issues = [i for i in jira_issues if i.get("action") == "reopened"]

        # 새로 생성된 이슈
        if created_issues:
            slack_message += f"➕ *새로 생성* ({len(created_issues)}개)\n"
            for issue in created_issues[:5]:  # 최대 5개만 표시
                issue_key = issue.get("key", "")
                test_name = issue.get("test", "")
                jira_issue_url = f"{JIRA_URL}/browse/{issue_key}"
                slack_message += f"   • <{jira_issue_url}|{issue_key}> - {test_name}\n"
            if len(created_issues) > 5:
                slack_message += f"   _...외 {len(created_issues) - 5}개_\n"

        # 기존 Open 이슈
        if existing_issues:
            slack_message += f"⏭️ *기존 Open* ({len(existing_issues)}개)\n"
            for issue in existing_issues[:3]:  # 최대 3개만 표시
                issue_key = issue.get("key", "")
                jira_issue_url = f"{JIRA_URL}/browse/{issue_key}"
                slack_message += f"   • <{jira_issue_url}|{issue_key}>\n"
            if len(existing_issues) > 3:
                slack_message += f"   _...외 {len(existing_issues) - 3}개_\n"

        # Reopen된 이슈
        if reopened_issues:
            slack_message += f"🔄 *Reopen* ({len(reopened_issues)}개)\n"
            for issue in reopened_issues[:3]:  # 최대 3개만 표시
                issue_key = issue.get("key", "")
                test_name = issue.get("test", "")
                jira_issue_url = f"{JIRA_URL}/browse/{issue_key}"
                slack_message += f"   • <{jira_issue_url}|{issue_key}> - {test_name}\n"
            if len(reopened_issues) > 3:
                slack_message += f"   _...외 {len(reopened_issues) - 3}개_\n"

        slack_message += "\n"

    # ============================================================
    # 검증 결과 (상태 변경된 이슈)
    # ============================================================
    if verification_results:
        closed_issues = [v for v in verification_results if v.get("action") == "closed"]

        if closed_issues:
            slack_message += "*✅ 검증 완료 (Close 처리)*\n"
            for issue in closed_issues:
                issue_key = issue.get("key", "")
                summary = issue.get("summary", "")
                previous = issue.get("previous_status", "RESOLVED")
                new = issue.get("new_status", "CLOSED")
                jira_issue_url = f"{JIRA_URL}/browse/{issue_key}"

                slack_message += f"   • <{jira_issue_url}|{issue_key}> - {summary}\n"
                slack_message += f"      상태: {previous} → {new}\n"

            slack_message += "\n"

    # ============================================================
    # Confluence 리포트 URL
    # ============================================================
    if confluence_url:
        slack_message += "*📊 상세 리포트*\n"
        slack_message += f"• <{confluence_url}|Confluence 리포트 보기> (팀 공유용)\n\n"

    # ============================================================
    # 파일별 상세 결과
    # ============================================================
    slack_message += "*📂 파일별 결과*\n"
    for file_display, tests in grouped_results.items():
        slack_message += f"*{file_display}*\n"
        for func_display, status in tests:
            if status == "PASS":
                slack_message += f"   └ ✅ {func_display}\n"
            elif status == "FAIL":
                slack_message += f"   └ ❌ {func_display}\n"
            elif status == "SKIP":
                slack_message += f"   └ ⚪ {func_display}\n"
        slack_message += "\n"

    return slack_message

def send_slack_message(message):
    """슬랙 메시지 전송"""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL 설정 없음")
        return False

    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            return True
        else:
            print(f"⚠️ 슬랙 전송 실패: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"❌ 슬랙 전송 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📤 슬랙 알림 전송 시작")
    print("=" * 60)

    # 데이터 로드
    test_results = load_test_results(RESULT_FILE)
    jira_issues = load_jira_issues()
    confluence_url = load_confluence_url()
    verification_results = load_verification_results()

    print(f"✅ 테스트 결과: {len(test_results)}개")
    print(f"✅ Jira 이슈: {len(jira_issues)}개")
    print(f"✅ Confluence URL: {'있음' if confluence_url else '없음'}")
    print(f"✅ 검증 결과: {len(verification_results)}개")

    # 메시지 구성
    slack_message = build_slack_message(test_results, jira_issues, confluence_url, verification_results)

    # 슬랙 전송
    success = send_slack_message(slack_message)

    if success:
        print("\n✅ 슬랙 알림이 전송되었습니다.")
    else:
        print("\n❌ 슬랙 알림 전송 실패")
