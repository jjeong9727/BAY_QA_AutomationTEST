import pytest
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account

PRODUCT_FILE_PATH = Path("product_name.json")

def get_undeletable_products():
    with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["kor"] for item in data if item.get("order_flag", 0) == 1]

def test_cannot_delete_product_with_order(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    undeletable_names = get_undeletable_products()
    if not undeletable_names:
        print("❌ order_flag = 1인 제품이 없습니다.")
        return

    target_name = undeletable_names[0]
    page.goto(URLS["bay_prdList"])
    page.fill("input[placeholder='제품명 검색']", target_name)
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    if rows.count() == 0:
        print(f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다.")
        return

    try:
        delete_button = page.locator("table tbody tr >> nth=0 >> td:nth-child(9) button").nth(1)
        delete_button.click()

        alert_popup = page.locator("div[role=alertdialog]")
        alert_popup.get_by_text("삭제", exact=True).click()
        page.wait_for_timeout(1000)

        alert = page.locator("data-testid=alert_using")
        assert alert.is_visible(), f"[FAIL] 삭제 불가 Alert 미표시 - 제품: {target_name}"
        print(f"[PASS][제품관리] order_flag=1 제품 삭제 불가 Alert 정상 노출: {target_name}")

    except Exception as e:
        raise Exception(f"[FAIL] 삭제 불가 테스트 실패\n에러 내용: {str(e)}")
