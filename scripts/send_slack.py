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
RESULT_FILE = "test_results.json"

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
            print(f"✅ 불러온 버전: {version}")  # 디버깅용
            return version
    except FileNotFoundError:
        print(f"❌ version_info.json 파일을 찾을 수 없음: {version_path}")
        return "버전 정보 없음"
    except json.JSONDecodeError:
        print(f"❌ version_info.json 파싱 실패: {version_path}")
        return "버전 정보 없음"
    
def load_test_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
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

def build_slack_message(test_results):
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

    # 헤더 부분
    slack_message = f":mega: *[CenturionBay] 자동화 테스트 결과* ({seoul_time})\n"
    slack_message += f"버전: :centurionlogo: `{version}`\n"
    slack_message += f"Total: {len(test_results)} | ✅ PASS: {success_count} | ❌ FAIL: {fail_count} | ⚪ SKIP: {skip_count}\n"
    slack_message += f":stopwatch: 전체 수행 시간: {total_time}\n\n"

    # 파일별 결과
    for file_display, tests in grouped_results.items():
        slack_message += f"*📂 {file_display}*\n"
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
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message to Slack: {response.status_code}, {response.text}")

if __name__ == "__main__":
    test_results = load_test_results(RESULT_FILE)
    slack_message = build_slack_message(test_results)
    send_slack_message(slack_message)
    print("✅ 슬랙 알림이 전송되었습니다.")
