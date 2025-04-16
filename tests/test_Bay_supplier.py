import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import  find_supplier_in_paginated_list



def test_register_supplier(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier = "자동화 업체명 등록 삭제 테스트용"
        manager = "매니저 이름 확인용"
        contact = "010-1234-5678"

        page.click("data-testid=btn_orderadd")
        page.wait_for_timeout(300)
        page.fill("data-testid=input_sup_name", supplier)
        page.wait_for_timeout(300)
        page.fill("data-testid=input_sup_manager", manager)
        page.wait_for_timeout(300)
        page.fill("data-testid=input_sup_contact", contact)
        page.wait_for_timeout(300)
        page.click("data-testid=btn_confirm")
        page.wait_for_timeout(1000)

        found = find_supplier_in_paginated_list(page, supplier, manager, contact)
        assert found, f"❌ 등록된 업체 정보가 리스트에서 확인되지 않음: {supplier}, {manager}, {contact}"
        print(f"[PASS] 업체 등록 및 리스트 확인 완료: {manager} ({contact})")


    except Exception as e:
        raise
