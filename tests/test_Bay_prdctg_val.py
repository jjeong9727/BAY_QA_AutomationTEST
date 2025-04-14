import pytest
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result  


def register_category(page: Page, tab_testid: str, name_kr: str, name_en: str):
    try:
        page.click(f"data-testid={tab_testid}")
        page.wait_for_timeout(300)
        page.click("data-testid=btn_add")
        page.locator("data-testid=input_kor").last.fill(name_kr)
        page.locator("data-testid=input_eng").last.fill(name_en)
        page.click("data-testid=btn_save")
    except Exception as e:
        error_message = f"Error in register_category: {str(e)}"
        save_test_result("register_category", error_message, status="ERROR")
        raise


def try_duplicate_registration(page: Page, tab_testid: str, name_kr: str, name_en: str):
    try:
        page.click(f"data-testid={tab_testid}")
        page.wait_for_timeout(1000)

        if page.locator("data-testid=btn_confirm").is_visible():
            page.click("data-testid=btn_confirm")
            page.wait_for_timeout(300)    


        page.click("data-testid=btn_add")
        page.locator("data-testid=input_kor").last.fill(name_kr)
        page.locator("data-testid=input_eng").last.fill(name_en)
        page.click("data-testid=btn_save")
        page.wait_for_timeout(500)

        
        assert page.locator("data-testid=alert_duplicate").is_visible(), "❌ 중복 알림 문구가 표시되지 않음"
        print(f"[PASS] 중복 등록 시 알림 문구 확인")

        save_test_result("test_register_supplier_duplicate", f"중복 등록 알림 문구 확인", status="PASS")

    except Exception as e:
        save_test_result("test_register_supplier_duplicate", f"중복 등록 실패: {str(e)}", status="FAIL")
        raise



def test_duplicate_category_names(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_category"])
    page.wait_for_timeout(3000)
    page.wait_for_url(URLS["bay_category"], timeout=60000)

    name_kr = "중복테스트"
    name_en1 = "DupOne"
    name_en2 = "DupTwo"

    # 구분
    # register_category(page, "tab_type", name_kr, name_en1)
    try_duplicate_registration(page, "tab_type", name_kr, name_en2)

    # 종류
    # register_category(page, "tab_group", name_kr, name_en1)
    try_duplicate_registration(page, "tab_category", name_kr, name_en2)

    # 제조사
    # register_category(page, "tab_maker", name_kr, name_en1)
    try_duplicate_registration(page, "tab_maker", name_kr, name_en2)
