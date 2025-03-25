import pytest
import requests
import os
import random
import time
import json
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account

# ✅ Slack Webhook 설정
SLACK_WEBHOOK_URL = URLS["slack_PV"] #private
# SLACK_WEBHOOK_URL = URLS["slack_CH"] #3명

# ✅ 실행 카운트를 저장할 파일 경로
COUNT_FILE = "run_count.txt"

def send_slack_message(message):
    """ Slack으로 메시지 전송"""
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    assert response.status_code == 200, "❌ Slack 메시지 전송 실패!"

def get_run_count():
    """ 실행 횟수를 불러오고 증가시키는 함수"""
    if not os.path.exists(COUNT_FILE):
        count = 1
    else:
        with open(COUNT_FILE, "r", encoding="utf-8") as f:  # 🔹 UTF-8 인코딩 지정
            count = int(f.read().strip()) + 1

    with open(COUNT_FILE, "w", encoding="utf-8") as f:  # 🔹 UTF-8 인코딩 지정
        f.write(str(count))

    return count

@pytest.fixture(scope="function")
def browser():
    """ Playwright 브라우저 실행 및 종료"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()



COUNT_FILE="Daily_count.json"
def get_daily_count():
    today = datetime.now().strftime("%Y-%m-%d")

    # 파일이 없으면 초기값 생성
    if not os.path.exists(COUNT_FILE):
        data = {"date": today, "count": 1}
    else:
        with open(COUNT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"date": today, "count": 1}

        if data.get("date") != today:
            data["date"] = today
            data["count"] = 1
        else:
            data["count"] += 1

    # 저장
    with open(COUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data["count"]

def generate_product_names():
    now = datetime.now()
    cnt= get_daily_count()

    date = now.strftime("%m%d_%H%M")
    count = f"{cnt:02d}"
    prdname_kor = f"등록테스트_{date}_{count}"
    prdname_eng = f"TestProduct_{date}_{count}"
    return prdname_kor, prdname_eng



# 1개 제품 등록 테스트
def test_register_product(browser):
    prdname_kor, prdname_eng = generate_product_names()

    page = browser.new_page()
    page.goto(URLS["bay_login"])

    # 로그인
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)

    page.click("data-testid=btn_addprd")
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    # ✅ 타입 선택 (드롭다운에서 랜덤 선택)
    page.click("data-testid=drop_type_trigger")
    page.wait_for_timeout(1000)  # 드롭다운이 열리는 시간 고려
    

    # 드롭다운 목록 가져오기
    type_options = page.locator("data-testid=drop_type_item").all_inner_texts()

    if type_options:
        random_index = random.randint(0, len(type_options) - 1)
        page.locator("data-testid=drop_type_item").nth(random_index).click()
    else:
        raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 제품 타입")

    #  카테고리 선택 (드롭다운에서 랜덤 선택)
    page.click("data-testid=drop_category_trigger")
    page.wait_for_timeout(1000)

    category_options = page.locator("data-testid=drop_category_item").all_inner_texts()

    if category_options:
        random_index = random.randint(0, len(category_options) - 1)
        page.locator("data-testid=drop_category_item").nth(random_index).click()
    else:
        raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 카테고리")

    #  제조사 선택 (드롭다운에서 랜덤 선택)
    page.click("data-testid=drop_maker_trigger")
    page.wait_for_timeout(1000)

    maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()

    if maker_options:
        random_index = random.randint(0, len(maker_options) - 1)
        page.locator("data-testid=drop_maker_item").nth(random_index).click()
    else:
        raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 제조사")

    #  제품명 입력
    page.fill("data-testid=input_prdname_kor", prdname_kor)
    page.fill("data-testid=input_prdname_eng", prdname_eng)

    try:
        #  저장 버튼 클릭
        page.click("data-testid=btn-save")

        #  제품 관리 페이지로 이동 완료 확인
        page.wait_for_url(URLS["bay_prdList"], timeout=10000)

        #  등록한 제품이 목록에 있는지 확인 (최대 10초 대기)
        product_exists = False
        for _ in range(10):
            if page.locator(f"text={prdname_kor}").count() > 0:
                product_exists = True
                break
            page.wait_for_timeout(1000)

        assert product_exists, f"❌ 제품 목록에서 {prdname_kor}을 찾을 수 없음"

        message = f"[Pass][제품관리] 1개 제품 등록 테스트"
        print(message)
        send_slack_message(message)

    except Exception as e:
        error_message = f"❌ 제품 등록 실패! 오류: {str(e)}"
        print(error_message)
        send_slack_message(error_message)
        raise

# 여러 제품 등록 테스트
def test_register_multiple_products(browser):
    # 등록할 제품 개수 (1~5개 사이 랜덤)
    num_products = random.randint(1, 5)

    
    product_data = []
    for _ in range(num_products):
        name_kor, name_eng = generate_product_names()
        product_data.append({
                "name_kor": name_kor,
                "name_eng": name_eng
        })


    page = browser.new_page()
    page.goto(URLS["bay_login"])

    #  로그인
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)

    page.click("data-testid=btn_addprd")
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    for idx, product in enumerate(product_data, start=1):
        #  제품 정보 입력 (최하단 행)

        ## 🔹 제품 타입 선택 (드롭다운에서 랜덤 선택)
        page.locator("data-testid=drop_type_trigger").last.click()
        page.wait_for_timeout(1000)

        type_options = page.locator("data-testid=drop_type_item").all_inner_texts()
        if type_options:
            random_index = random.randint(0, len(type_options) - 1)
            page.locator("data-testid=drop_type_item").nth(random_index).click()
        else:
            raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 제품 타입")

        ## 🔹 카테고리 선택 (드롭다운에서 랜덤 선택)
        page.locator("data-testid=drop_category_trigger").last.click()
        page.wait_for_timeout(1000)

        category_options = page.locator("data-testid=drop_category_item").all_inner_texts()
        if category_options:
            random_index = random.randint(0, len(category_options) - 1)
            page.locator("data-testid=drop_category_item").nth(random_index).click()
        else:
            raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 카테고리")

        ## 🔹 제조사 선택 (드롭다운에서 랜덤 선택)
        page.locator("data-testid=drop_maker_trigger").last.click()
        page.wait_for_timeout(1000)

        maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()
        if maker_options:
            random_index = random.randint(0, len(maker_options) - 1)
            page.locator("data-testid=drop_maker_item").nth(random_index).click()
        else:
            raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 제조사")

        # 제품명 입력
        page.locator("data-testid=input_prdname_kor").last.fill(product["name_kor"])
        page.locator("data-testid=input_prdname_eng").last.fill(product["name_eng"])

        if idx < num_products:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.wait_for(state="visible", timeout=5000)

            # 버튼이 활성화될 때까지 대기 후 클릭 (문제 해결)
            assert add_row_button.is_visible(), "❌ 추가 버튼이 화면에 표시되지 않음!"
            add_row_button.click(force=True)

    try:
        # 저장 버튼 클릭
        page.click("data-testid=btn-save")

        # 제품 관리 페이지로 이동 완료 확인
        page.wait_for_url(URLS["bay_prdList"], timeout=10000)
        page.reload()
        page.wait_for_timeout(3000)  # 페이지 새로고침 후 3초 대기

        # 등록한 모든 제품명이 현재 페이지에 존재하는지 확인
        for product in product_data:
            product_locator = page.locator(f"text={product['name_kor']}")
            product_locator.wait_for(state="visible", timeout=5000)  # 제품명이 보일 때까지 대기

            assert product_locator.is_visible(), f"❌ 등록한 제품이 목록에 없음: {product['name_kor']}"

        # Slack 알림 전송
        message = f"[PASS][제품관리] {num_products}개 제품 등록 테스트"
        print(message)
        send_slack_message(message)


    except Exception as e:
        error_message = f"❌ 제품 등록 실패! 오류: {str(e)}"
        print(error_message)
        send_slack_message(error_message)
        raise






