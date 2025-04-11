import pytest
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result  

PRODUCT_FILE_PATH = Path("product_name.json")

def get_undeletable_products():
    try:
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [item["kor"] for item in data if item.get("order_flag", 0) == 1]
    except Exception as e:
        error_message = f"Error while fetching undeletable products: {str(e)}"
        save_test_result("get_undeletable_products", error_message, status="ERROR")
        raise

def test_delete_product_validation(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    try:
        undeletable_names = get_undeletable_products()
        if not undeletable_names:
            fail_msg = "❌ order_flag = 1인 제품이 없습니다."
            save_test_result("test_delete_product_validation", fail_msg, status="FAIL")
            print(fail_msg)
            return

        target_name = undeletable_names[0]
        page.goto(URLS["bay_prdList"])
        page.fill("data-testid=input_search']", target_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            fail_msg = f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다."
            save_test_result("test_delete_product_validation", fail_msg, status="FAIL")
            print(fail_msg)
            return

        delete_button = page.locator("table tbody tr >> nth=0 >> td:nth-child(9) button").nth(1)
        delete_button.click()

        alert_popup = page.locator("div[role=alertdialog]")
        alert_popup.get_by_text("삭제", exact=True).click()
        page.wait_for_timeout(1000)

        alert = page.locator("data-testid=alert_using")
        assert alert.is_visible(), f"[FAIL] 삭제 불가 Alert 미표시 - 제품: {target_name}"
        success_msg = f"[PASS][제품관리] order_flag=1 제품 삭제 불가 Alert 정상 노출: {target_name}"
        print(success_msg)
        save_test_result("test_delete_product_validation", success_msg, status="PASS")

    except Exception as e:
        fail_msg = f"[FAIL] 삭제 불가 테스트 실패\n에러 내용: {str(e)}"
        save_test_result("test_delete_product_validation", fail_msg, status="FAIL")
        print(fail_msg)
        raise
