from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import get_all_product_names


def get_existing_supplier_info():
    all_data = get_all_product_names()
    for item in reversed(all_data):
        if item.get("supplier") == "자동화 업체명":
            return item["supplier"], item["manager"], item["contact"]
    return None, None, None


def test_register_supplier_duplicate(browser):
    page = browser.new_page()
    page.goto(URLS["login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_supplier"])
    page.wait_for_url(URLS["bay_supplier"], timeout=60000)

    # 기존 발주처 정보 가져오기
    supplier, manager, contact = get_existing_supplier_info()
    assert supplier and manager and contact, "❌ 기존 발주처 정보가 없습니다. 선행 등록 필요"

    # 중복 등록 시도
    page.click("data-testid=btn_orderadd")
    page.fill("data-testid=input_sup_name", supplier)
    page.fill("data-testid=input_sup_manager", manager)
    page.fill("data-testid=input_sup_contact", contact)
    page.click("data-testid=btn_confirm")
    page.wait_for_timeout(500)

    # 중복 알림 확인
    assert page.locator("data-testid=alert_duplicate").is_visible(), "❌ 중복 알림 문구가 표시되지 않음"
    print(f"[PASS] 중복 등록 시 알림 문구 노출 확인: {supplier} / {manager}")
