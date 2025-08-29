from playwright.sync_api import Page, expect
from config import URLS
from typing import Optional 
from helpers.common_utils import bay_login
from datetime import datetime, timedelta
import re
from helpers.order_status_utils import search_order_history
from helpers.approve_status_data import approve_status_map
def assert_time_equal(expected: str, actual: str):
    fmt = "%Y. %m. %d %H:%M"

    # UI 값 정리 (NBSP → 일반 공백, 여러 공백을 하나로)
    actual = actual.replace("\xa0", " ").strip()
    actual = re.sub(r"\s+", " ", actual)

    expected_dt = datetime.strptime(expected, fmt)
    actual_dt = datetime.strptime(actual, fmt)

    assert expected_dt == actual_dt, (
        f"❌ 승인 요청일 불일치\n기대: {expected_dt}, 실제: {actual_dt}"
    )

    assert expected_dt == actual_dt, f"❌ 승인 요청 시간 불일치 (expected={expected}, actual={actual})"
def check_order_pending_history(page:Page, rule:str, product:str, status:str, manual:bool, group:Optional[bool]=None):
    page.wait_for_timeout(3000)
    page.locator("data-testid=drop_rules_trigger").click()
    page.locator("data-testid=drop_rules_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rules_item", has_text=rule).click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    if manual: # 수동 발주
        expect(page.locator("data-testid=history")).not_to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)
    else : # 자동 발주
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)
        rows = page.locator('table tbody tr')

        product_cell = rows.last.locator('td:nth-child(2)') # 1행 2열 (제품명)
        product_text = product_cell.inner_text().strip()
        if group: # 통합 발주 
            products = ["배치 확인 제품 1", "배치 확인 제품 2", "배치 확인 제품 3", 
            "배치 확인 제품 4", "배치 확인 제품 5", "배치 확인 제품 6", 
            "배치 확인 제품 7", "배치 확인 제품 8", "배치 확인 제품 9", "발주 삭제 제품 1", "발주 삭제 제품 2"] # 발주 삭제 제품 1, 2도 통합내역 이므로 확인 리스트에 포함
            # 줄바꿈, 공백 정리
            normalized_text = product_text.replace("\n", " ").strip()

            # startswith 로 대표 제품명 확인
            assert any(normalized_text.startswith(p) for p in products), \
                f"대표행의 제품명이 예상 목록과 다름, 노출값: {normalized_text}"
        else: # 개별 발주 
            product_text = product_text
            assert product_text == product, f"제품명이 다름 (기대 값: {product}, 노출 값:{product_text})"

    page.locator("data-testid=btn_reset").click() #검색 결과 초기화 
    page.wait_for_timeout(2000)
# 승인 요청 내역 생성 확인 
def check_approval_history(page: Page, status: str, product: str, 
                           *, auto: Optional[bool] = None, rule: Optional[str] = None, time: Optional[str] = None,):

    page.wait_for_timeout(3000)
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name=status, exact=True).click()
    page.wait_for_timeout(500)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    if auto is True: # 수동 발주 + 승인 규칙
        rows = page.locator('table tbody tr')
        test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).first
        rule_cell = test_row.locator("td:nth-child(7)") # 1행 7열 (규칙명)
        rule_text = rule_cell.inner_text().strip()
        approve_time = test_row.locator('td:nth-child(11)') # 1행 11열 (승인 요청일)
        approve_time_text = approve_time.inner_text().strip()
        assert rule == rule_text, f"규칙명이 다름 (기대 값: {rule}, 노출 값: {rule_text})"
        assert_time_equal(time, approve_time_text) # 승인 요청일 비교
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000)
    elif auto is False: # 배치 발주 + 승인 규칙
        rows = page.locator('table tbody tr')
        test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).first
        rule_cell = test_row.locator('td:nth-child(7)') # 1행 7열 (규칙명)
        rule_text = rule_cell.inner_text().strip()
        approve_time = test_row.locator('td:nth-child(11)') # 1행 11열 (승인 요청일)
        approve_time_text = approve_time.inner_text().strip()
        assert rule == rule_text, f"규칙명이 다름 (기대 값: {rule}, 노출 값: {rule_text})"
        assert_time_equal(time, approve_time_text) # 승인 요청일 비교
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000)
    else: # 수동 발주 + 자동 승인 => 바로 발주 내역에 생성됨 
        expect(page.locator("data-testid=history")).not_to_be_visible(timeout=5000)
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)

        search_order_history(page, product, "발주 요청")

# 발주 예정 내역 검색 
def search_order_pending_history(page:Page, order_rule: str, product: str):
    page.goto(URLS["bay_order_pending"])
    page.wait_for_selector("data-testid=drop_rules_trigger", timeout=10000)
    page.locator("data-testid=drop_rules_trigger").click()
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
    page.goto(URLS["bay_approval"])
    page.wait_for_selector("data-testid=drop_status_trigger", timeout=10000)
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_selector("data-testid=drop_status_item", timeout=10000)
    page.get_by_role("option", name=status, exact=True).click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(3000)
# 승인 요청 내역에서 approve_id 가져오기
def get_approve_id_from_approve_list(page:Page, product:str):
    rows = page.locator('table tbody tr')
    row_count = rows.count()
    for i in range(row_count):
        row = rows.nth(i)
        product_cell = row.locator("td:nth-child(2)")
        product_text = product_cell.inner_text().strip()

        if product in product_text:
            approve_div = row.locator("div[data-testid='order']")
            approve_id = approve_div.get_attribute("data-orderid")
            return approve_id

    raise ValueError(f"승인 요청 리스트에서 {product} 제품을 찾을 수 없음")


# 발주 예정 내역, 승인 요청 내역 버튼 상태 확인 
def check_approval_status_buttons(page:Page, status:str, product:str, order_rule:str, bulk:bool, approve:bool):
    conditions = approve_status_map[status]
    expected_status = conditions["status_text"]
    
    if approve is True :  # 승인 요청 내역 
        search_order_approval_history(page, expected_status, product)
        rows = page.locator('table tbody tr')
        test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).first
        product_cell = test_row.locator('td:nth-child(2)') # 제품행 2열 (제품명)
            
        product_text = product_cell.inner_text().strip()
        assert product_text == product, f"제품명이 다름 (기대 값: {product}, 실제 값: {product_text})"
        
        status_cell = test_row.locator('td:nth-child(1)') # 승인 요청 내역 제품행 1열 (승인 상태)
        rule_cell = test_row.locator('td:nth-child(7)') # 승인 요청 내역 제품행 7열 (발주 규칙)
        buttons = test_row.locator("td").nth(-1) # 승인 요청 내역 제품행 마지막열 (승인/거절 버튼)

        status_text = status_cell.inner_text().strip()
        rule_text = rule_cell.inner_text().strip()
        assert status_text == expected_status, f"상태 값이 다름 (기대: {expected_status}, 실제: {status_text})"
        assert rule_text == order_rule, f"발주 규칙이 다름 (기대 값: {order_rule}, 실제 값: {rule_text})"
        reject_button = buttons.locator("data-testid=btn_reject")
        approve_button = buttons.locator("data-testid=btn_approve")

    elif approve is False:  # 발주 예정 내역 
        search_order_pending_history(page, order_rule, product)
        if bulk : # 통합 내역 
            page.locator("data-testid=btn_detail").last.click()
            page.wait_for_timeout(2000)
            rows = page.locator('table tbody tr')
            test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).last 
            product_cell = test_row.locator("td:nth-child(2)")

        else: # 개별 내역
            rows = page.locator('table tbody tr')
            test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).last
            product_cell = test_row.locator('td:nth-child(2)') # 공통 1행 2열 (제품명)

        product_text = product_cell.inner_text().strip()
        assert product_text == product, f"제품명이 다름 (기대 값: {product}, 실제 값: {product_text})"

        status_cell = test_row.locator('td:nth-child(8)') # 발주 예정 내역 1행 8열 (승인 상태)
        edit_button = test_row.locator("data-testid=btn_edit").nth(0)
        delete_button = test_row.locator("data-testid=btn_edit").nth(1)

        buttons = test_row.locator("td").nth(-1) # 발주 예정 내역 1행 마지막열 (수정/삭제 버튼)

        status_button = status_cell.locator("data-testid=btn_approval")
        status_text = status_cell.inner_text().strip()
        delete_button = buttons.locator("data-testid=btn_edit", has_text="삭제")
        edit_button   = buttons.locator("data-testid=btn_edit", has_text="수정")


    for key, value in conditions.items():
        if key == "status_text":
            assert status_text == expected_status, f"상태 값이 다름 (기대 값: {expected_status}, 실제 값: {status_text})"
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