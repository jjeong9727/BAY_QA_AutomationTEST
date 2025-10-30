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
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Anthropic 클라이언트 초기화
anthropic_client = None
if ANTHROPIC_API_KEY:
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✅ Claude AI 연결 완료")
    except ImportError:
        print("⚠️ anthropic 패키지 없음 (pip install anthropic)")
    except Exception as e:
        print(f"⚠️ Claude AI 초기화 실패: {e}")

# Jira 상태 정의
OPEN_STATUSES = ["OPEN", "PENDING", "IN PROGRESS", "REOPENED", "DEV 배포"]
RESOLVED_STATUSES = ["RESOLVED", "CLOSED"]

def extract_label_from_filename(filename):
    """
    test_Bay_login.py → login
    tests/test_Bay_product.py → product
    """
    basename = os.path.basename(filename)
    if "test_Bay_" in basename:
        label = basename.replace("test_Bay_", "").replace(".py", "")
        return label
    return "unknown"

def search_existing_issues(label):
    """
    모든 상태의 이슈 중 automation + label 매칭 검색
    JQL: project = BAY AND labels = "automation" AND labels = "login"
    """
    jql = f'project = {PROJECT_KEY} AND labels = "automation" AND labels = "{label}"'

    url = f"{JIRA_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "fields": "key,status,summary"
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

def get_issue_status_name(issue):
    """이슈의 상태명 추출"""
    return issue.get("fields", {}).get("status", {}).get("name", "")

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
            print(f"  ✅ 코멘트 추가 완료: {issue_key}")
            return True
        else:
            print(f"  ⚠️ 코멘트 추가 실패: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ 코멘트 추가 오류: {e}")
        return False

def reopen_issue(issue_key):
    """이슈를 REOPENED 상태로 전환"""
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

        # 2. "Reopen" transition 찾기
        reopen_transition = None
        for t in transitions:
            if "reopen" in t.get("name", "").lower():
                reopen_transition = t.get("id")
                break

        if not reopen_transition:
            print(f"  ⚠️ Reopen transition을 찾을 수 없음: {issue_key}")
            return False

        # 3. Reopen 실행
        payload = {"transition": {"id": reopen_transition}}
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            print(f"  ✅ Reopen 완료: {issue_key}")
            return True
        else:
            print(f"  ⚠️ Reopen 실패: {response.status_code}, {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Reopen 오류: {e}")
        return False

def load_version():
    """tests/version_info.json에서 버전 정보 로드"""
    version_path = os.path.join("tests", "version_info.json")
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "버전 정보 없음")
    except:
        return "버전 정보 없음"

def create_issue(summary, description, labels, version):
    """새 Jira 이슈 생성"""
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
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            },
            "issuetype": {"name": "Bug"},
            "labels": labels,
            "priority": {"name": "Medium"}
        }
    }

    # 버전 필드 추가 (선택사항 - Jira 프로젝트에 버전 필드가 있을 경우)
    # 없으면 에러 발생할 수 있으므로 주석 처리
    # if version:
    #     payload["fields"]["versions"] = [{"name": version}]

    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            issue_key = response.json().get("key")
            print(f"  ✅ 새 이슈 생성: {issue_key}")
            return issue_key
        else:
            print(f"  ❌ Jira 등록 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ 이슈 생성 오류: {e}")
        return None

def get_screen_display_name(label):
    """화면명 한글화"""
    screen_name_map = {
        "login": "로그인",
        "alert": "공통",
        "supplier": "업체관리",
        "category": "카테고리관리",
        "rule_order": "발주규칙",
        "rule_approval": "승인규칙",
        "product": "제품관리",
        "product_upload_validation": "제품업로드",
        "product_upload": "제품업로드",
        "rule_order_apply_bulk": "발주규칙일괄적용",
        "product_edit": "제품수정",
        "stock_in": "입고",
        "stock_out": "출고",
        "order_pending": "발주예정내역",
        "order_approval": "발주승인내역",
        "order_status": "발주내역",
        "order_status_batch": "발주내역",
        "stock_history": "재고상세"
    }
    return screen_name_map.get(label, label.capitalize())

def generate_summary_with_ai(test_name, message, label):
    """
    Claude AI로 Jira 이슈 제목 생성
    """
    if not anthropic_client:
        # AI 사용 불가 시 fallback
        return None

    screen_display = get_screen_display_name(label)

    prompt = f"""다음 테스트 실패 정보를 보고 Jira 이슈 제목을 생성해주세요.

테스트명: {test_name}
에러 메시지: {message}
화면: {screen_display}

조건:
- 형식: [자동화][{screen_display}] 간단한 현상 설명
- 40자 이내
- 한글로 작성
- 기술적인 에러 코드(AssertionError 등)는 제외하고 실제 현상만 설명
- 사용자 관점에서 이해하기 쉽게

예시:
- [자동화][로그인] 관리자 계정 로그인 실패
- [자동화][제품 관리] 제품 등록 시 필수 항목 검증 오류
- [자동화][발주 승인] 발주 거절 처리 실패

제목만 출력:"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"  ⚠️ AI 제목 생성 실패: {e}")
        return None

def generate_description_with_ai(test_name, file_name, message, stack, version, label):
    """
    Claude AI로 Jira 이슈 상세 설명 생성
    """
    if not anthropic_client:
        # AI 사용 불가 시 fallback
        return None

    screen_display = get_screen_display_name(label)

    prompt = f"""다음 테스트 실패 정보를 보고 Jira 이슈 설명을 생성해주세요.

테스트명: {test_name}
파일: {file_name}
화면: {screen_display}
에러: {message}
스택: {stack[:500]}  # 너무 길면 일부만
버전: {version}

다음 형식으로 작성해주세요:

Test Environment
빌드 버전: {version}

Step
(테스트명과 에러를 분석하여 실제 사용자가 수행할 재현 스텝을 1~3단계로 추론)

Actual Result
(에러 메시지를 기반으로 실제 발생한 현상을 사용자 관점에서 설명)

Expected Result
(정상 동작을 1~2문장으로 설명)

Note
테스트 파일: {file_name}
에러 메시지: {message}

Stack Trace:
{stack}

조건:
- 모든 강조 마크업(h3, ■, *, - 등) 사용 금지, 일반 텍스트만 사용
- Step은 실제 사용자 행동으로 작성 (예: "로그인 페이지 접속", "제품 등록 버튼 클릭")
- Actual Result는 기술적 에러가 아닌 사용자가 보는 현상으로 작성
- 한글로 작성
- 기술 용어는 최소화

설명:"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"  ⚠️ AI 설명 생성 실패: {e}")
        return None

def generate_summary(label, message):
    """
    Jira 이슈 제목 생성 (Fallback)

    형식: [자동화] [화면명] 간단한 현상 설명
    예시: [자동화] [로그인] 관리자 계정 로그인 실패
    """
    screen_display = get_screen_display_name(label)

    # 에러 메시지에서 핵심 내용 추출
    if ":" in message:
        core_message = message.split(":")[-1].strip()
    else:
        core_message = message[:50] if len(message) > 50 else message

    return f"[자동화] [{screen_display}] {core_message}"

def generate_description(test_name, file_name, message, stack, version):
    """
    Jira 이슈 상세 설명 생성 (Fallback)

    형식:
    Test Environment
    빌드 버전: v1.2.0-rc.10

    Step
    1. 테스트 실행

    Actual Result
    1. 테스트 실패

    Expected Result
    1. 테스트 통과

    Note
    테스트 파일: tests/test_Bay_login.py
    에러 메시지: AssertionError
    Stack Trace: ...
    """
    description = f"""Test Environment
빌드 버전: {version}

Step
1. {test_name} 테스트 실행

Actual Result
1. 테스트 실패

Expected Result
1. 테스트 통과

Note
테스트 파일: {file_name}
에러 메시지: {message}

Stack Trace:
{stack}"""

    return description

def register_failed_issues_from_summary(summary_path="test_results.json"):
    """
    실패한 테스트를 Jira에 등록 (중복 방지 + 상태별 처리)

    로직:
    1. 모든 상태의 이슈 검색 (automation + label)
    2. OPEN 상태 → 번호만 기록
    3. RESOLVED/CLOSED → 코멘트 + Reopen
    4. 없음 → 새 이슈 생성
    """
    if not os.path.exists(summary_path):
        print(f"❌ 테스트 결과 파일 없음: {summary_path}")
        return []

    with open(summary_path, "r", encoding="utf-8") as f:
        test_results = json.load(f)

    # 버전 정보 로드
    version = load_version()
    print(f"✅ 버전: {version}")

    jira_issues = []  # 최종 Jira 이슈 목록

    for test in test_results:
        if test.get("status", "").upper() != "FAIL":
            continue

        test_name = test.get("test_name", "")
        file_name = test.get("file", "")
        message = test.get("message", "")
        stack = test.get("stack", "")

        print(f"\n🔍 처리 중: {test_name}")

        # Label 추출
        label = extract_label_from_filename(file_name)
        labels = ["automation", label]

        print(f"  📌 Labels: {labels}")

        # 기존 이슈 검색 (모든 상태)
        existing_issues = search_existing_issues(label)

        if existing_issues:
            # 동일 이슈 존재
            issue = existing_issues[0]
            issue_key = issue["key"]
            status_name = get_issue_status_name(issue)

            print(f"  🔗 기존 이슈 발견: {issue_key} (상태: {status_name})")

            if status_name in OPEN_STATUSES:
                # OPEN/PENDING/IN PROGRESS/REOPENED/DEV 배포 → 아무 작업 안함
                print(f"  ⏭️ 이미 Open 상태 → 작업 없음")
                jira_issues.append({
                    "key": issue_key,
                    "test": test_name,
                    "file": file_name,
                    "action": "existing_open",
                    "status": status_name
                })

            elif status_name in RESOLVED_STATUSES:
                # RESOLVED/CLOSED → 코멘트 + Reopen
                print(f"  🔄 해결됨 상태 → 코멘트 추가 및 Reopen")
                comment = f"🔄 재현됨\n\n테스트: {test_name}\n파일: {file_name}\n에러: {message}"
                add_comment_to_issue(issue_key, comment)
                reopen_issue(issue_key)

                jira_issues.append({
                    "key": issue_key,
                    "test": test_name,
                    "file": file_name,
                    "action": "reopened",
                    "status": "REOPENED"
                })
            else:
                # 기타 상태 (있을 경우 대비)
                print(f"  ⚠️ 알 수 없는 상태: {status_name}")
                jira_issues.append({
                    "key": issue_key,
                    "test": test_name,
                    "file": file_name,
                    "action": "unknown_status",
                    "status": status_name
                })
        else:
            # 중복 없음 → 새 이슈 생성
            print(f"  ➕ 기존 이슈 없음 → 새 이슈 생성")

            # AI로 Summary와 Description 생성 시도
            summary = None
            description = None

            if anthropic_client:
                print(f"  🤖 AI로 제목/설명 생성 중...")
                summary = generate_summary_with_ai(test_name, message, label)
                description = generate_description_with_ai(test_name, file_name, message, stack, version, label)

            # AI 실패 시 Fallback
            if not summary:
                print(f"  📝 정형화 방식으로 제목 생성")
                summary = generate_summary(label, message)

            if not description:
                print(f"  📝 정형화 방식으로 설명 생성")
                description = generate_description(test_name, file_name, message, stack, version)

            print(f"  📝 제목: {summary}")

            issue_key = create_issue(summary, description, labels, version)

            if issue_key:
                jira_issues.append({
                    "key": issue_key,
                    "test": test_name,
                    "file": file_name,
                    "action": "created",
                    "status": "OPEN"
                })

    # 생성된 이슈 목록 저장 (Slack, Confluence에서 사용)
    output_path = "jira_created_issues.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jira_issues, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Jira 이슈 처리 완료: {len(jira_issues)}개")
    print(f"📁 저장 위치: {output_path}")

    return jira_issues

if __name__ == "__main__":
    print("=" * 60)
    print("📌 Jira 이슈 자동 등록 시작")
    print("=" * 60)

    try:
        issues = register_failed_issues_from_summary()

        # 요약 출력
        print("\n" + "=" * 60)
        print("📊 처리 결과 요약")
        print("=" * 60)

        created = [i for i in issues if i["action"] == "created"]
        existing = [i for i in issues if i["action"] == "existing_open"]
        reopened = [i for i in issues if i["action"] == "reopened"]

        print(f"  ➕ 새로 생성: {len(created)}개")
        print(f"  ⏭️ 기존 Open: {len(existing)}개")
        print(f"  🔄 Reopen: {len(reopened)}개")
        print(f"  📝 총 처리: {len(issues)}개")

    except Exception as e:
        print(f"\n❌ 실행 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()
