import pytest
import random
import requests
from playwright.sync_api import Page
from config import URLS, Account

# Slack Webhook
# SLACK_WEBHOOK_URL = URLS["slack_PV"] #private
SLACK_WEBHOOK_URL = URLS["slack_CH"] #3명

def send_slack_message(message: str):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    assert response.status_code == 200, "❌ Slack 메시지 전송 실패"

def test_duplicate_product_name(browser):
    EXISTING_NAME_KOR = "등록테스트_중복확인"
    EXISTING_NAME_ENG = "TestProduct_Duplicate"

    page: Page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    # 제품 등록 페이지 이동
    page.goto(URLS["bay_prdAdd"])
    page.wait_for_timeout(1000)


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

    # ✅ 카테고리 선택 (드롭다운에서 랜덤 선택)
    page.click("data-testid=drop_category_trigger")
    page.wait_for_timeout(1000)

    category_options = page.locator("data-testid=drop_category_item").all_inner_texts()

    if category_options:
        random_index = random.randint(0, len(category_options) - 1)
        page.locator("data-testid=drop_category_item").nth(random_index).click()
    else:
        raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 카테고리")

    # ✅ 제조사 선택 (드롭다운에서 랜덤 선택)
    page.click("data-testid=drop_maker_trigger")
    page.wait_for_timeout(1000)

    maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()

    if maker_options:
        random_index = random.randint(0, len(maker_options) - 1)
        page.locator("data-testid=drop_maker_item").nth(random_index).click()
    else:
        raise Exception("❌ 드롭다운 옵션을 찾을 수 없음: 제조사")

    # 제품명 입력
    page.fill("data-testid=input_prdname_kor", EXISTING_NAME_KOR)
    page.fill("data-testid=input_prdname_eng", EXISTING_NAME_ENG)

    # 저장 버튼 클릭
    page.click("data-testid=btn-save")
    page.wait_for_timeout(1000)

    # 경고 메시지 확인
    try:
        alert = page.locator('[role="status"]', has_text="이미 존재합니다.").first
        assert alert.is_visible(), f"[FAIL][제품등록] 중복 제품명 경고 미표시: {EXISTING_NAME_KOR}"
        msg = f"[PASS][제품등록] Validation 제품명 중복 테스트 ('{EXISTING_NAME_KOR}')"
        print(msg)
        send_slack_message(msg)

    except Exception as e:
        fail_msg = f"[FAIL][제품등록] Validation 제품병 중복 테스트 실패)\n에러: {str(e)}"
        print(fail_msg)
        send_slack_message(fail_msg)
        raise
