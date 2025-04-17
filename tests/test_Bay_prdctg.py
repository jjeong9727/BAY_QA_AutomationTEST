import pytest
import requests
import random
from playwright.sync_api import Page
from config import URLS, Account

def generate_name(prefix):
    return f"{prefix}{random.randint(1000, 9999)}"

def login_and_go_to_add_page(page: Page):
    try:
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")

        page.wait_for_url(URLS["bay_home"])
        page.goto(URLS["bay_category"])
        page.wait_for_url(URLS["bay_category"])
        page.wait_for_timeout(1500)
    except Exception as e:
        error_message = f"Error in login_and_go_to_add_page: {str(e)}"
        raise

@pytest.mark.parametrize("tab,testid_kor,testid_eng,require_eng", [
    ("tab_type", "input_kor", "input_eng", True),     # 구분
    ("tab_category", "input_kor", "input_eng", True), # 종류
    ("tab_maker", "input_kor", "input_eng", False),   # 제조사
])
def test_register_category_each(browser, tab, testid_kor, testid_eng, require_eng):
    page: Page = browser.new_page()
    login_and_go_to_add_page(page)

    try:
        page.click(f"data-testid={tab}")
        page.click("data-testid=btn_add")
        page.wait_for_timeout(300)
        name_kr = generate_name("자동화등록_한글")
        page.locator(f"data-testid={testid_kor}").last.fill(name_kr)

        if require_eng:
            name_en = generate_name("Auto_ENG")
            page.locator(f"data-testid={testid_eng}").last.fill(name_en)

        page.click("data-testid=btn_save")
        page.wait_for_timeout(3000)

        # 스크롤을 끝까지 내려서 확인
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

        # input_kor 항목 중 name_kr와 동일한 값이 있는지 확인
        input_kor_locator = page.locator(f"input[data-testid={testid_kor}]")
        found = False
        for i in range(input_kor_locator.count()):
            item_value = input_kor_locator.nth(i).input_value()
            if item_value == name_kr:
                found = True
                break

        # 결과에 따라 PASS/FAIL 판단
        assert found, f"❌ 등록 항목 미노출: {name_kr}"
        msg = f"[PASS][카테고리] {tab} 등록 후 리스트 노출 확인 성공 ({name_kr})"
        print(msg)
    except Exception as e:
        fail_msg = f"[FAIL][카테고리] {tab} 등록 후 리스트 미노출\n에러: {str(e)}"
        print(fail_msg)
        raise
