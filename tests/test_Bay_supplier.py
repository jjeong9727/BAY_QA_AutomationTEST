import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import is_duplicate_supplier_from_product_file, find_supplier_in_paginated_list
from helpers.save_test_result import save_test_result  
def generate_manager_name():
    try:
        suffix = random.randint(1000, 9999)
        return f"담당자{suffix}"
    except Exception as e:
        save_test_result("generate_manager_name", f"담당자 이름 생성 실패: {str(e)}", status="FAIL")
        raise


def test_register_supplier(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier = "자동화 업체명"
        manager = generate_manager_name()
        contact = "010-6275-4153"

        if is_duplicate_supplier_from_product_file(manager, contact):
            print(f"[SKIP] 이미 등록된 발주처: {supplier}, {manager}, {contact}")
            save_test_result("test_register_supplier", f"이미 등록된 발주처: {supplier}, {manager}, {contact}", status="SKIP")
            return

        page.click("data-testid=btn_orderadd")
        page.fill("data-testid=input_sup_name", supplier)
        page.fill("data-testid=input_sup_manager", manager)
        page.fill("data-testid=input_sup_contact", contact)
        page.click("data-testid=btn_confirm")
        page.wait_for_timeout(1000)

        found = find_supplier_in_paginated_list(page, supplier, manager, contact)
        assert found, f"❌ 등록된 발주처 정보가 리스트에서 확인되지 않음: {supplier}, {manager}, {contact}"
        print(f"[PASS] 발주처 등록 및 리스트 확인 완료: {manager} ({contact})")

        save_test_result("test_register_supplier", f"발주처 등록 및 리스트 확인 완료: {manager} ({contact})", status="PASS")

    except Exception as e:
        save_test_result("test_register_supplier", f"발주처 등록 실패: {str(e)}", status="FAIL")
        raise
