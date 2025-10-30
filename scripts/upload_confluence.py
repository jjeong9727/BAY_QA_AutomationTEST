import os
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "CENBAY")
CONFLUENCE_PARENT_PAGE_ID = os.getenv("CONFLUENCE_PARENT_PAGE_ID")

def load_test_results(file_path="test_results.json"):
    """테스트 결과 로드"""
    if not os.path.exists(file_path):
        print(f"❌ 테스트 결과 파일 없음: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_jira_issues(file_path="jira_created_issues.json"):
    """Jira 이슈 목록 로드"""
    if not os.path.exists(file_path):
        print(f"⚠️ Jira 이슈 파일 없음: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_confluence_content(test_results, jira_issues):
    """
    Confluence 페이지 콘텐츠 생성 (Storage Format)
    """
    # 통계 계산
    total = len(test_results)
    passed = sum(1 for t in test_results if t.get("status") == "PASS")
    failed = sum(1 for t in test_results if t.get("status") == "FAIL")
    skipped = sum(1 for t in test_results if t.get("status") == "SKIP")

    # 실행 시간 계산
    total_duration = 0.0
    for t in test_results:
        try:
            duration_str = t.get("duration", "0초").replace("초", "")
            total_duration += float(duration_str)
        except:
            continue

    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)
    duration_text = f"{minutes}분 {seconds}초"

    # Jira 이슈 매핑 (file → issue_key)
    jira_map = {}
    for issue in jira_issues:
        file_name = issue.get("file", "")
        jira_map[file_name] = issue

    # Storage Format 시작
    content = f"""
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>📊 테스트 통계</strong></p>
    <p>Total: {total} | ✅ PASS: {passed} | ❌ FAIL: {failed} | ⏭️ SKIP: {skipped}</p>
    <p>⏱️ 전체 수행 시간: {duration_text}</p>
    <p>📅 실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>📝 테스트 결과 상세</h2>

<table>
  <thead>
    <tr>
      <th>파일명</th>
      <th>테스트명</th>
      <th>상태</th>
      <th>시간</th>
      <th>Jira 이슈</th>
    </tr>
  </thead>
  <tbody>
"""

    # 파일별로 그룹핑
    grouped = {}
    for result in test_results:
        file_name = result.get("file", "")
        if file_name not in grouped:
            grouped[file_name] = []
        grouped[file_name].append(result)

    # 테이블 행 생성
    for file_name, tests in grouped.items():
        for test in tests:
            test_name = test.get("test_name", "")
            status = test.get("status", "")
            duration = test.get("duration", "")

            # 상태 아이콘
            if status == "PASS":
                status_icon = "✅ PASS"
            elif status == "FAIL":
                status_icon = "❌ FAIL"
            else:
                status_icon = "⏭️ SKIP"

            # Jira 이슈 링크
            jira_link = ""
            if file_name in jira_map:
                issue = jira_map[file_name]
                issue_key = issue.get("key", "")
                if issue_key:
                    jira_url = f"{CONFLUENCE_URL.replace('/wiki', '')}/browse/{issue_key}"
                    jira_link = f'<a href="{jira_url}">{issue_key}</a>'

            content += f"""
    <tr>
      <td>{os.path.basename(file_name)}</td>
      <td>{test_name}</td>
      <td>{status_icon}</td>
      <td>{duration}</td>
      <td>{jira_link}</td>
    </tr>
"""

    content += """
  </tbody>
</table>
"""

    # Jira 이슈 목록 추가
    if jira_issues:
        content += """
<h2>🐞 생성된 Jira 이슈</h2>
<table>
  <thead>
    <tr>
      <th>이슈 키</th>
      <th>테스트명</th>
      <th>파일</th>
      <th>처리 결과</th>
    </tr>
  </thead>
  <tbody>
"""

        for issue in jira_issues:
            issue_key = issue.get("key", "")
            test_name = issue.get("test", "")
            file_name = os.path.basename(issue.get("file", ""))
            action = issue.get("action", "")

            # Action 한글화
            action_text = {
                "created": "➕ 새로 생성",
                "existing_open": "⏭️ 기존 Open",
                "reopened": "🔄 Reopen"
            }.get(action, action)

            if issue_key:
                jira_url = f"{CONFLUENCE_URL.replace('/wiki', '')}/browse/{issue_key}"
                content += f"""
    <tr>
      <td><a href="{jira_url}">{issue_key}</a></td>
      <td>{test_name}</td>
      <td>{file_name}</td>
      <td>{action_text}</td>
    </tr>
"""

        content += """
  </tbody>
</table>
"""

    return content

def create_confluence_page(title, content):
    """
    Confluence 페이지 생성

    Returns:
        str: 생성된 페이지 URL
    """
    url = f"{CONFLUENCE_URL}/rest/api/content"

    payload = {
        "type": "page",
        "title": title,
        "space": {
            "key": CONFLUENCE_SPACE_KEY
        },
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }

    # Parent Page ID가 있으면 추가
    if CONFLUENCE_PARENT_PAGE_ID:
        payload["ancestors"] = [{"id": CONFLUENCE_PARENT_PAGE_ID}]

    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            page_data = response.json()
            page_id = page_data.get("id")
            page_url = f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={page_id}"
            print(f"✅ Confluence 페이지 생성 완료: {page_url}")
            return page_url
        else:
            print(f"❌ Confluence 페이지 생성 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Confluence 업로드 오류: {e}")
        return None

def upload_test_report():
    """
    테스트 결과를 Confluence에 업로드

    Returns:
        str: Confluence 페이지 URL
    """
    print("=" * 60)
    print("📤 Confluence 리포트 업로드 시작")
    print("=" * 60)

    # 1. 테스트 결과 로드
    test_results = load_test_results()
    if not test_results:
        print("❌ 테스트 결과가 없습니다.")
        return None

    # 2. Jira 이슈 로드
    jira_issues = load_jira_issues()

    # 3. 페이지 제목 생성
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"[BAY] 자동화 테스트 결과 - {timestamp}"

    print(f"📝 페이지 제목: {title}")

    # 4. 콘텐츠 생성
    content = build_confluence_content(test_results, jira_issues)

    # 5. Confluence 페이지 생성
    page_url = create_confluence_page(title, content)

    if page_url:
        # 6. URL 저장
        with open("confluence_report_url.txt", "w", encoding="utf-8") as f:
            f.write(page_url)

        print(f"\n✅ Confluence 업로드 완료!")
        print(f"📊 리포트 URL: {page_url}")

        return page_url
    else:
        return None

if __name__ == "__main__":
    try:
        url = upload_test_report()

        if url:
            print("\n" + "=" * 60)
            print("✅ 성공")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 실패")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ 실행 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()
