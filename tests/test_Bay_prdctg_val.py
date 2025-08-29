import pytest
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login

def try_duplicate_registration(page: Page, tab_testid: str, name_kr: str, name_en: str):
    try:
        page.click(f"data-testid={tab_testid}")
        page.wait_for_timeout(2000)

        if page.locator("data-testid=btn_confirm").is_visible():
            page.click("data-testid=btn_confirm")
            page.wait_for_timeout(3000)    

        page.click("data-testid=btn_add")
        page.wait_for_timeout(2000)
        page.locator("data-testid=input_kor").last.fill(name_kr)
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_eng").last.fill(name_en)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_save")
        page.wait_for_timeout(500)
        page.locator("data-testid=alert_duplicate").wait_for(timeout=5000)

        expect(page.locator("data-testid=alert_duplicate")).to_be_visible(timeout=3000)
        print(f"[PASS] 중복 등록 토스트 확인")

        # 사용중인 카테고리 삭제 시도
        name_kr_locator = page.locator(f"input[data-testid='input_kor']").first
        item_to_delete = None
        item_value_to_delete = None
        row_index = -1
        count = name_kr_locator.count()
        for i in reversed(range(count)):
            item_text = name_kr_locator.nth(i).input_value()
            if "중복테스트" in item_text:
                item_to_delete = name_kr_locator.nth(i)
                item_value_to_delete = item_text
                row_index = i
                break

        if item_to_delete:
            delete_buttons = page.locator("button[data-testid='btn_delete']")
            target_button = delete_buttons.nth(row_index)
            target_button.click()
            # expect(page.locator("txt_delete")).to_be_visible(timeout=3000)
            # page.wait_for_timeout(500)
            # page.locator("data-testid=btn_comfirm").click()
            expect(page.locator("alert_using")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

    except Exception as e:
        raise


def test_duplicate_category_names(page):
    bay_login(page)

    page.goto(URLS["bay_category"])
    page.wait_for_url(URLS["bay_category"], timeout=6000)
    page.wait_for_timeout(1500)

    name_kr = "중복 확인용"
    name_en1 = "DupOne"
    name_en2 = "DupTwo"

    # 구분
    try_duplicate_registration(page, "tab_type", name_kr, name_en2)
    # 종류
    try_duplicate_registration(page, "tab_category", name_kr, name_en2)

    # 제조사
    try_duplicate_registration(page, "tab_maker", name_kr, name_en2)

    
