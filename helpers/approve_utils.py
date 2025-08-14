from playwright.sync_api import Page, expect
from config import URLS
from typing import Optional 
from helpers.common_utils import bay_login
import re
from helpers.order_status_utils import search_order_history
from helpers.approve_status_data import approve_status_map

# 발주 예정 내역 
def check_order_pending_history(page:Page, rule:str, product:str, manual:bool, group:Optional[bool]=None):
    page.locator("data-testid=drop_rules_trigger").click()
    page.wait_for_selector("data-testid=drop_rules_search", timeout=3000)
    page.locator("data-testid=drop_rules_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rules_item", has_text=rule).click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()

    if manual: # 수동 발주
        expect(page.locator("data-testid=btn_approval")).not_to_be_visible(timeout=5000)
        page.wait_for_timeout(1000)
    else : # 자동 발주
        expect(page.locator("data-testid=btn_approval")).to_be_visible(timeout=5000)
        page.wait_for_timeout(1000)
        rows = page.locator('table tbody tr')
        status_cell = rows.nth(0).locator('td:nth-child(8)') # 1행 8열 (상태값)
        status_text = status_cell.inner_text().strip()
        assert status_text == rule, f"승인 상태가 다름 (기대 값: {rule}, 노출 값: {status_text})"
        product_cell = rows.nth(0).locator('td:nth-child(2)') # 1행 2열 (제품명)
        product_text = product_cell.inner_text().strip()
        if group: # 통합 발주 
            products = ["자동화제품_1", "자동화제품_2", "자동화제품_3", 
            "자동화제품_4", "자동화제품_5", "자동화제품_6", 
            "자동화제품_7", "자동화제품_8", "자동화제품_9"]
            product_text = re.split(r"\s*외\s*", product_text)[0].strip()
            assert product_text in products, f"대표행이 다름 (기대 값: {product_text} 외 2건)"
        else: # 개별 발주 
            product_text = product_text
            assert product_text == product, f"제품명이 다름 (기대 값: {product}, 노출 값:{product_text})"

    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)
# 승인 요청 내역 생성 확인 
def check_approval_history(page: Page, status: str, product: str, 
                           *, auto: Optional[bool] = None, rule: Optional[str] = None, time: Optional[str] = None,):

    status_map = {"승인 대기": "status_2", "발주 승인": "status_3", "발주 거절": "status_4"}
    status_key = status_map.get(status, "status_1")

    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_selector("data-testid=drop_status_1", timeout=3000)
    page.locator(f"data-testid=drop_{status_key}").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    if auto is True: # 수동 발주 + 승인 규칙
        rows = page.locator('table tbody tr')
        rule_cell = rows.nth(0).locator('td:nth-child(7)') # 1행 7열 (규칙명)
        rule_text = rule_cell.inner_text()
        order_time = rows.nth(0).locator('td:nth-child(8)') # 1행 8열 (발주 예정일)
        order_time_text = order_time.inner_text().strip()
        auto_rule = "수동 발주"
        auto_order = "승인 완료 후 즉시 발주"
        assert auto_rule == rule_text, f"규칙명이 다름 (기대 값: {auto_rule}, 노출 값: {rule_text})"
        assert auto_order == order_time_text, f"발주 예정일이 다름 (기대 값: {auto_order}, 노출 값: {order_time_text})"
        page.wait_for_timeout(1000)
    elif auto is False: # 자동 발주 + 승인 규칙
        rows = page.locator('table tbody tr')
        rule_cell = rows.nth(0).locator('td:nth-child(7)') # 1행 7열 (규칙명)
        rule_text = rule_cell.inner_text().strip()
        order_time = rows.nth(0).locator('td:nth-child(8)') # 1행 8열 (발주 예정일)
        order_time_text = order_time.inner_text().strip()
        assert rule == rule_text, f"규칙명이 다름 (기대 값: {rule}, 노출 값: {rule_text})"
        assert time == order_time_text, f"발주 예정일이 다름 (기대 값: {time}, 노출 값: {order_time_text})"
        page.wait_for_timeout(1000)
    else: # 수동 발주 + 자동 승인 => 바로 발주 내역에 생성됨 
        expect(page.locator("data-testid=history")).to_be_visible(timeout=5000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)

        search_order_history(page, product, "발주 요청")
# 발주 예정 내역 검색 
def search_order_pending_history(page:Page, order_rule: str, product: str):
    page.locator("data-testid=drop_rules_trigger").click()
    page.wait_for_selector("data-testid=drop_rules_search", timeout=3000)
    page.locator("data-testid=drop_rules_search").fill(order_rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rules_item", has_text=order_rule).click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(3000)
# 승인 요청 내역 검색 
def search_order_approval_history(page:Page, status:str, product:str):
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_selector("data-testid=drop_status_item", timeout=3000)
    page.locator("data-testid=drop_status_item", has_text=status).click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(3000)
# 승인 요청 내역에서 approve_id 가져오기
def get_approve_id_from_approve_list(page:Page, product:str):
    rows = page.locator('table tbody tr')
    for row in rows:
        # 해당 행에서 제품명이 일치하는지 확인
        row_product_locator = row.locator("td").nth(1).locator("p")
        row_product_name = row_product_locator.inner_text().strip()
        print(f"🔍 검색된 제품명: {row_product_name}")

        # 제품명이 일치하는지 비교
        if row_product_name == product:
            # 제품명이 일치하면 해당 행에서 approve_id 추출
            approve_id = row.locator("td[data-testid='approve']").first.get_attribute('data-approve')
            print(f"✅ 찾은 approve_id: {approve_id}")
            return approve_id
# 발주 예정 내역, 승인 요청 내역 버튼 상태 확인 
def check_approval_status_buttons(page:Page, status:str, product:str, order_rule:str, bulk:bool, approve:bool):
    conditions = approve_status_map[status]
    
    if approve:  # 승인 요청 내역 
        search_order_pending_history(page, order_rule, product)
        if bulk : # 통합 내역 
            page.locator("data-testid=btn_detail").click()
            rows = page.locator('table tbody tr')
            expect(rows.nth(3)).to_be_visible(timeout=5000)

            top4 = page.locator("table tbody tr:nth-child(-n+4)")
            candidates = top4.filter(has=page.locator("td:nth-child(2)", has_text=product))
            expect(candidates.first).to_be_visible(timeout=3000)  

            test_row = candidates.first
            product_cell = test_row.locator("td:nth-child(2)")

        else: # 개별 내역
            rows = page.locator('table tbody tr')
            test_row = rows.nth(0)
            product_cell = test_row.locator('td:nth-child(2)') # 공통 1행 2열 (제품명)
            

        product_text = product_cell.inner_text().strip()
        assert product_text == product, f"제품명이 다름 (기대 값: {product}, 실제 값: {product_text})"
        
        status_cell = test_row.locator('td:nth-child(1)') # 승인 요청 내역 1행 1열 (승인 상태)
        rule_cell = test_row.locator('td:nth-child(7)') # 승인 요청 내역 1행 7열 (발주 규칙)
        buttons = test_row.locator("td").nth(-1) # 승인 요청 내역 1행 마지막열 (승인/거절 버튼)

        status_text = status_cell.inner_text().strip()
        rule_text = rule_cell.inner_text().strip()
        assert rule_text == order_rule, f"제품명이 다름 (기대 값: {order_rule}, 실제 값: {rule_text})"
        reject_button = buttons.locator("data-testid=btn_reject")
        approve_button = buttons.locator("data-testid=btn_approve")

    else:  # 발주 요청 내역 
        search_order_approval_history(page, status, product)
        if bulk : # 통합 내역 
            page.locator("data-testid=btn_detail").click()
            rows = page.locator('table tbody tr')
            expect(rows.nth(3)).to_be_visible(timeout=5000)

            top4 = page.locator("table tbody tr:nth-child(-n+4)")
            candidates = top4.filter(has=page.locator("td:nth-child(2)", has_text=product))
            expect(candidates.first).to_be_visible(timeout=3000)  

            test_row = candidates.first
            product_cell = test_row.locator("td:nth-child(2)")

        else: # 개별 내역
            rows = page.locator('table tbody tr')
            test_row = rows.nth(0)
            product_cell = test_row.locator('td:nth-child(2)') # 공통 1행 2열 (제품명)

        product_text = product_cell.inner_text().strip()
        assert product_text == product, f"제품명이 다름 (기대 값: {product}, 실제 값: {product_text})"

        status_cell = test_row.locator('td:nth-child(8)') # 발주 예정 내역 1행 8열 (승인 상태)
        buttons = test_row.locator("td").nth(-1) # 발주 예정 내역 1행 마지막열 (수정/삭제 버튼)

        status_button = status_cell.locator("data-testid=btn_approval")
        status_text = status_cell.inner_text().strip()
        edit_button = buttons.locator("data-testid=btn_edit")
        delete_button = buttons.locator("data-testid=btn_delete")

    for key, value in conditions.items():
        if key == "status_text":
            assert status_text == status, f"상태 값이 다름 (기대 값: {status}, 실제 값: {status_text})"
        if key == "status_enabled": 
            if value:
                expect(status_button).to_be_enabled()
            else :
                expect(status_button).to_be_disabled()
        if key == "edit_enabled":
            if value:
                expect(edit_button).to_be_enabled()
            else :
                expect(edit_button).to_be_disabled()
        if key == "delete_enabled":
            if value:
                expect(delete_button).to_be_enabled()
            else :
                expect(delete_button).to_be_disabled()
        if key == "approve_enabled":
            if value:
                expect(approve_button).to_be_enabled()
            else :
                expect(approve_button).to_be_disabled()
        if key == "reject_enabled":
            if value:
                expect(reject_button).to_be_enabled()
            else :
                expect(reject_button).to_be_disabled()