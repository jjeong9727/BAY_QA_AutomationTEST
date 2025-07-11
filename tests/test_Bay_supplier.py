import random
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.product_utils import  find_supplier_in_paginated_list
from helpers.common_utils import bay_login 



def test_register_supplier(page):
    try:
        bay_login(page)
        
        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier = "자동화 업체명 등록 삭제 테스트용"
        manager = "매니저 이름 확인용"
        contact = "01012345678"
        memo = "자동화 테스트로 업체명 등록 확인 합니다. 바로 삭제 테스트에 활용할거예요."

        page.click("data-testid=btn_orderadd")
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_name", supplier)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_manager", manager)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_contact", contact)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_memo", memo)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_confirm")
        expect(page.locator("data-testid=alert_register")).to_be_visible(timeout=3000)


        found = find_supplier_in_paginated_list(page, supplier, manager, contact, memo)
        assert found, f"❌ 등록된 업체 정보가 리스트에서 확인되지 않음: {supplier}, {manager}, {contact}"
        print(f"[PASS] 업체 등록 및 리스트 확인 완료: {manager} ({contact})")


    except Exception as e:
        raise

def test_edit_supplier(page):
    bay_login(page)
    page.goto(URLS["bay_supplier"])
    page.wait_for_url(URLS["bay_supplier"], timeout=60000)

    supplier = "자동화 업체명 등록 삭제 테스트용"
    new_supplier = "수정 자동화 업체명"
    new_manager = "수정 매니저 이름"
    new_contact = "01087654321"
    new_memo = "자동화 테스트로 업체 정보 수정 확인 합니다. 바로 삭제 테스트에 활용할거예요."

    page.fill("data-testid=input_search", supplier)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_edit").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_cancel").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").click()
    page.wait_for_timeout(1000)
    
    page.fill("data-testid=input_sup_name", new_supplier)
    page.wait_for_timeout(500)
    page.fill("data-testid=input_sup_manager", new_manager)
    page.wait_for_timeout(500)
    page.fill("data-testid=input_sup_contact", new_contact)
    page.wait_for_timeout(500)
    page.fill("data-testid=input_memo", new_memo)
    page.wait_for_timeout(500)
    page.click("data-testid=btn_confirm")
    expect(page.locator("data-testid=alert_edit")).to_be_visible(timeout=3000)
