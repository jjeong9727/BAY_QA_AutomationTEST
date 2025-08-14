import json
import os
from typing import Optional 
from datetime import datetime
from config import URLS, Account
from playwright.sync_api import Page  

# 결과를 저장할 파일 경로
TEST_RESULTS_FILE = 'test_results.json'

# # 테스트 결과 저장 함수
# def save_test_result(test_name, message, status="FAIL"):
#     # 결과를 저장할 데이터
#     result_data = {
#         "test_name": test_name,
#         "status": status,
#         "message": message,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     }

#     # 기존 결과 불러오기
#     if os.path.exists(TEST_RESULTS_FILE):
#         with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
#             results = json.load(f)
#     else:
#         results = []

#     # 새로운 결과 추가
#     results.append(result_data)

#     # 결과 파일에 저장
#     with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
#         json.dump(results, f, ensure_ascii=False, indent=2)




def get_product_stock(product_name):
    # 실제 재고 조회 로직
    return 10  # 예시 값

def update_product_flag(product_name, flag):
    # 실제 제품 상태 업데이트 로직
    print(f"[공통] 제품 플래그 업데이트: {product_name} → {flag}")

import os
from datetime import datetime

# 카운트를 저장할 파일 경로
COUNT_FILE_PATH = "daily_count.json"

def get_daily_count():
    # 현재 날짜를 가져와서 날짜 포맷을 설정
    today = datetime.now().strftime("%Y-%m-%d")

    # 파일에 저장된 날짜가 오늘인지 확인
    if os.path.exists(COUNT_FILE_PATH):
        with open(COUNT_FILE_PATH, "r") as file:
            last_date, count = file.read().split(",")
            # 날짜가 같으면 카운트를 증가시키고 반환
            if last_date == today:
                count = str(int(count) + 1)  # 카운트 증가
                with open(COUNT_FILE_PATH, "w") as file:
                    file.write(f"{today},{count}")
                return int(count)
    
    # 만약 파일이 없거나 날짜가 다르면 카운트 초기화
    with open(COUNT_FILE_PATH, "w") as file:
        file.write(f"{today},1")  # 오늘 날짜와 1부터 시작하는 카운트 저장
    
    return 1  # 처음 카운트가 1부터 시작

import json

def clean_product_json(file_path="product_name.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered = [item for item in data if item.get("delivery_status") == 6]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)

        print(f"✅ delivery_status == 6 항목만 유지 완료 (총 {len(filtered)}개)")

    except FileNotFoundError:
        print("⚠️ product_name.json 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ JSON 처리 중 오류 발생: {e}")

def bay_login(page: Page, account: Optional[str] = None,):
    page.goto(URLS["bay_login"])
    
    # ✅ 로그인 페이지 로딩 확인: 최대 5초 대기
    try:
        page.wait_for_selector('[data-testid="input_id"]', timeout=5000)
    except:
        print("⚠️ input_id 요소가 5초 안에 로드되지 않아 새로고침 시도")
        page.reload()
        page.wait_for_selector('[data-testid="input_id"]', timeout=5000)


    if account : 
        id = f"{account}@medisolveai.com"
    else:
        id = Account["testid"]

    # ✅ 로그인 입력
    page.fill('[data-testid="input_id"]', id)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_pw"]', Account["testpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(3000)