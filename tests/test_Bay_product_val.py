import pytest
import random
import json
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.product_utils import get_latest_product_name, load_saved_product_names
from helpers.common_utils import bay_login
def test_duplicate_product_name(page):
    try:
        item = get_latest_product_name()
        prdname_kor = "중복테스트"
        prdname_eng = "Duplicate Test"

        bay_login(page)

        page.goto(URLS["bay_prdList"])
        expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=7000)
        page.locator("data-testid=btn_addprd").click()
        expect(page.locator("data-testid=drop_type_trigger")).to_be_visible(timeout=7000)
        page.wait_for_timeout(500)

        # 구분 선택
        page.locator("data-testid=drop_type_trigger").last.click()
        expect(page.locator("data-testid=drop_type_item")).to_be_visible(timeout=5000)
        page.wait_for_timeout(500)
        type_items = page.locator("data-testid=drop_type_item")
        type_index = random.randint(0, type_items.count() - 1)
        selected_type = type_items.nth(type_index).inner_text().strip()
        type_items.nth(type_index).click()

        # 종류 선택
        page.locator("data-testid=drop_group_trigger").last.click()
        expect(page.locator("data-testid=drop_group_item")).to_be_visible(timeout=5000)
        page.wait_for_timeout(500)
        group_items = page.locator("data-testid=drop_group_item")
        group_index = random.randint(0, group_items.count() - 1)
        selected_group = group_items.nth(group_index).inner_text().strip()
        group_items.nth(group_index).click()
        page.wait_for_timeout(500)
        
        # 제품명 생성 및 입력
        page.fill("data-testid=input_prdname_kor", prdname_kor)
        page.wait_for_timeout(500)
        page.fill("data-testid=input_prdname_eng", prdname_eng)
        page.wait_for_timeout(500)

        # 제조사 선택
        page.locator("data-testid=drop_maker_trigger").last.click()
        expect(page.locator("data-testid=drop_maker_item")).to_be_visible(timeout=5000)
        page.wait_for_timeout(500)
        maker_items = page.locator("data-testid=drop_maker_item")
        maker_index = random.randint(0, maker_items.count() - 1)
        selected_maker = maker_items.nth(maker_index).inner_text().strip()
        maker_items.nth(maker_index).click()
        page.wait_for_timeout(500)

        page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
        page.wait_for_timeout(500)
        safety = 5
        page.locator("data-testid=input_stk_safe").last.fill(str(safety))
        page.wait_for_timeout(500)
        auto_order = 10
        page.locator("data-testid=input_stk_qty").last.fill(str(auto_order))
        page.wait_for_timeout(500)

        # 업체 선택
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_supplier_trigger").last.click()
        expect(page.locator("data-testid=drop_supplier_item")).to_be_visible(timeout=5000)
        page.wait_for_timeout(500)
        supplier_items = page.locator("data-testid=drop_supplier_item")
        automation_supplier = supplier_items.locator("text=자동화업체") 
        automation_supplier.click(force=True)
        page.wait_for_timeout(500)

        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_save").click()
        # page.locator("button:has-text('완료')").click()
        
        expect(page.locator("data-testid=alert_duplicate")).to_be_visible(timeout=4000)
        page.wait_for_timeout(500)

        print(f"[PASS] 중복 제품명 확인")

    except Exception as e:
        print(f"❌ 중복 테스트 실패: {str(e)}")
        raise


