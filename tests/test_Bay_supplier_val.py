from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result 
import random

def test_register_supplier_duplicate(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier_name = "중복테스트"
        manager_name = "중복테스트"
        contact_info = "01012345678"
        
        print(f"선택된 업체: {supplier_name}, 담당자: {manager_name}, 연락처: {contact_info}")

        # 2. 선택한 업체 정보로 중복 등록 시도
        page.click("data-testid=btn_orderadd")  # 업체 등록 모달 열기
        page.fill("data-testid=input_sup_name", supplier_name)  # 업체명 입력
        page.fill("data-testid=input_sup_manager", manager_name)  # 담당자 입력
        page.fill("data-testid=input_sup_contact", contact_info)  # 연락처 입력
        page.click("data-testid=btn_confirm")  # 완료 버튼 클릭
        page.wait_for_timeout(500)

        # 3. 중복 알림 확인
        assert page.locator("data-testid=alert_duplicate").is_visible(), "❌ 중복 알림 문구가 표시되지 않음"
        print(f"[PASS] 중복 등록 시 알림 문구 노출 확인: {supplier_name} / {manager_name}")

        save_test_result("test_register_supplier_duplicate", f"중복 등록 알림 문구 확인: {supplier_name} / {manager_name}", status="PASS")

    except Exception as e:
        save_test_result("test_register_supplier_duplicate", f"중복 등록 실패: {str(e)}", status="FAIL")
        raise
