import pytest
import random
import json
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import get_latest_product_name, load_saved_product_names
def test_duplicate_product_name(browser):
    try:
        
        item = get_latest_product_name()
        prdname_kor = item["kor"]
        prdname_eng = item["eng"]

        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_prdAdd"])
        page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

        # 구분 선택
        page.locator("data-testid=drop_type_trigger").last.click()
        page.wait_for_timeout(1000)
        type_items = page.locator("data-testid=drop_type_item")
        type_index = random.randint(0, type_items.count() - 1)
        selected_type = type_items.nth(type_index).inner_text().strip()
        type_items.nth(type_index).click()

        # 종류 선택
        page.locator("data-testid=drop_group_trigger").last.click()
        page.wait_for_timeout(1000)
        group_items = page.locator("data-testid=drop_group_item")
        group_index = random.randint(0, group_items.count() - 1)
        selected_group = group_items.nth(group_index).inner_text().strip()
        group_items.nth(group_index).click()
        
        # 제품명 생성 및 입력
        page.fill("data-testid=input_prdname_kor", prdname_kor)
        page.fill("data-testid=input_prdname_eng", prdname_eng)

        prdnames=[]
        prdnames.append(prdname_kor)

        # 제조사 선택
        page.locator("data-testid=drop_maker_trigger").last.click()
        page.wait_for_timeout(1000)
        maker_items = page.locator("data-testid=drop_maker_item")
        maker_index = random.randint(0, maker_items.count() - 1)
        selected_maker = maker_items.nth(maker_index).inner_text().strip()
        maker_items.nth(maker_index).click()

        page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
        safety = 5
        page.locator("data-testid=input_stk_safe").last.fill(str(safety))
        auto_order = 10
        page.locator("data-testid=input_stk_qty").last.fill(str(auto_order))

        # 업체 선택
        page.locator("data-testid=drop_supplier_trigger").last.click()
        page.wait_for_timeout(1000)
        supplier_items = page.locator("data-testid=drop_supplier_item")
        automation_supplier = supplier_items.locator("text=자동화업체")  # 자동화 테스트 안정성을 위해 지정
        automation_supplier.click()

        # page.click("data-testid=btn-save")
        page.locator("button:has-text('완료')").click()
        page.wait_for_timeout(500)
        alert = page.locator("data-testid=alert_duplicate")
        assert alert.is_visible(), "❌ 중복 경고 메시지가 표시되지 않음"
        print(f"[PASS][제품관리] 중복 제품명 등록 방지 확인됨: {prdname_kor}")

    except Exception as e:
        print(f"❌ 중복 테스트 실패: {str(e)}")
        raise


