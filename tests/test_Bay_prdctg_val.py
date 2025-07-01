import pytest
from playwright.sync_api import Page
from config import URLS, Account
from helpers.common_utils import bay_login

def try_duplicate_registration(page: Page, tab_testid: str, name_kr: str, name_en: str):
    try:
        page.click(f"data-testid={tab_testid}")
        page.wait_for_timeout(5000)

        if page.locator("data-testid=btn_confirm").is_visible():
            page.click("data-testid=btn_confirm")
            page.wait_for_timeout(3000)    

        page.click("data-testid=btn_add")
        page.wait_for_timeout(3000)
        page.locator("data-testid=input_kor").last.fill(name_kr)
        page.wait_for_timeout(3000)
        page.locator("data-testid=input_eng").last.fill(name_en)
        page.wait_for_timeout(3000)
        page.click("data-testid=btn_save")
        page.wait_for_timeout(500)
        page.locator("data-testid=alert_duplicate").wait_for(timeout=5000)

        assert page.locator("data-testid=alert_duplicate").is_visible(), "❌ 중복 알림 문구가 표시되지 않음"
        print(f"[PASS] 중복 등록 시 알림 문구 확인")

    except Exception as e:
        raise

def test_duplicate_category_names(page):
    bay_login(page)

    page.goto(URLS["bay_category"])
    page.wait_for_url(URLS["bay_category"], timeout=6000)

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
