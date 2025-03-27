import pytest
import random
import requests
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import get_latest_product_name

def test_duplicate_product_name(browser):
    from helpers.product_utils import get_latest_product_name

    item = get_latest_product_name()
    prdname_kor = item["kor"]
    prdname_eng = item["eng"]
    supplier = item["supplier"]
    type_name = item["type"]

    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    # 구분 선택
    page.click("data-testid=drop_type_trigger")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text=type_name).click()

    # 종류 선택 (랜덤)
    page.click("data-testid=drop_category_trigger")
    page.wait_for_timeout(1000)
    category_options = page.locator("data-testid=drop_category_item").all_inner_texts()
    page.locator("data-testid=drop_category_item").nth(random.randint(0, len(category_options)-1)).click()

    # 제조사 선택 (랜덤)
    page.click("data-testid=drop_maker_trigger")
    page.wait_for_timeout(1000)
    maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()
    page.locator("data-testid=drop_maker_item").nth(random.randint(0, len(maker_options)-1)).click()

    # 공급업체 선택
    page.click("data-testid=drop_supplier")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text=supplier).click()

    # 업체 연락처 선택
    page.click("data-testid=drop_contact")
    page.wait_for_timeout(1000)
    contact_options = page.locator("data-testid=drop_contact_item").all_inner_texts()
    page.locator("data-testid=drop_contact_item").nth(random.randint(0, len(contact_options)-1)).click()

    # 제품명 입력
    page.fill("data-testid=input_prdname_kor", prdname_kor)
    page.fill("data-testid=input_prdname_eng", prdname_eng)

    # 단가 / 재고 입력
    page.fill("data-testid=input_price", "1234")
    page.fill("data-testid=input_stk_safe", "10")
    page.fill("data-testid=input_stk_qty", "20")

    try:
        page.click("data-testid=btn-save")
        page.wait_for_timeout(2000)
        alert = page.locator("data-testid=alert_duplicate")
        assert alert.is_visible(), "❌ 중복 경고 메시지가 표시되지 않음"
        print(f"[PASS][제품관리] 중복 제품명 등록 방지 확인됨: {prdname_kor}")

    except Exception as e:
        print(f"❌ 중복 테스트 실패: {str(e)}")
        raise
