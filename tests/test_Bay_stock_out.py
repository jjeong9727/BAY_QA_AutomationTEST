from __future__ import annotations
from base64 import urlsafe_b64decode
import random
import time
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Optional
from playwright.sync_api import TimeoutError, expect
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag
from helpers.common_utils import bay_login
from helpers.order_status_utils import search_order_history
from helpers.approve_utils import check_approval_history, check_order_pending_history

order_rules=["자동화규칙_개별","자동화규칙_묶음"]
products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3"]
reject_products = ["발주 거절 제품 1", "발주 거절 제품 2"]
ordered_product = []
# 수동 발주 
def test_stock_manual_order(page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)

    products = ["수동 발주 제품 1", "수동 발주 제품 2", "수동 발주 제품 3"]
    expected_rules = ["승인규칙_1명", "승인규칙_n명", "자동 승인"]
    price = "5000"
    quantity = "10"
    expected_amount = "50,000"
    expected_supplier = "자동화업체D, 권정의D 010-6275-4153"

    # 재고 가져오기 
        # 수동 발주 제품_1 
    page.locator("data-testid=input_search").fill(products[0])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock1 = stock_cell.inner_text()

        # 수동 발주 제품_2
    page.locator("data-testid=input_search").fill(products[1])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock2 = stock_cell.inner_text()

    # 수동 발주 제품_3
    page.locator("data-testid=input_search").fill(products[2])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock3 = stock_cell.inner_text()

    expected_list = [expected_stock1, expected_stock2, expected_stock3]

    # 수동 발주 (수동 발주 제품_1, 2, 3)
    page.locator("data-testid=btn_order").click()
    page.wait_for_selector("data-testid=drop_prdname_trigger", timeout=10000)
    for idx, product in enumerate(products, start=1):
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_selector("data-testid=drop_prdname_search", timeout=3000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)

        current_stock = page.locator("data-testid=txt_current_stock").last.input_value().strip()
        assert current_stock == expected_list[idx-1], f"재고가 일치하지 않음 (기대 값:{expected_list[idx-1]}, 노출 값: {current_stock})"
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_price").last.fill(price)
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_qty").last.fill(quantity)
        page.wait_for_timeout(1000)

        amount= page.locator("data-testid=txt_amount").last.input_value().strip()
        supplier = page.locator("data-testid=txt_supplier").last.input_value().strip()
        rule = page.locator("data-testid=txt_rule").last.input_value().strip()
        
        assert amount == expected_amount, f"발주 금액이 일치하지 않음 (기대 값:{expected_amount}, 노출 값: {amount})"
        assert supplier == expected_supplier, f"업체명이 일치하지 않음 (기대 값:{expected_supplier}, 노출 값: {supplier})"
        assert rule == expected_rules[idx-1], f"승인 규칙이 일치하지 않음 (기대 값:{expected_rules[idx-1]}, 노출 값: {rule})"

        if idx < len(products):
            page.locator("data-testid=btn_addrow").click()
            page.wait_for_timeout(1000) 
        
    # 저장 

    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("수동 발주를 진행하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=txt_amount").last).to_have_value(expected_amount, timeout=3000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("수동 발주를 진행하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_manual")).to_have_text("수동 발주가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)
        # 현재 시간 저장 (제품 별로)
    
    now_str = datetime.now().strftime("%Y. %m. %d %H:%M")
    
    # 승인 요청 내역 노출 확인 
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)
    check_approval_history(page, "승인 대기", products[0], auto=True, rule="수동 발주", time=now_str)
    check_approval_history(page, "승인 대기", products[1], auto=True, rule="수동 발주", time=now_str)
    check_approval_history(page, "승인 대기", products[2], auto=None, rule="수동 발주") # 발주 내역 생성 확인 

# 배치 시간 계산 후 JSON에 저장
def get_safe_batch_time() -> datetime:
    now = datetime.now()
    minute = now.minute

    # 다다음 배치 (10분 단위 기준)
    next_block = (minute // 10 + 3) * 10
    next_hour = now.hour

    if next_block >= 60:
        next_block -= 60
        next_hour = (next_hour + 1) % 24

    next_time = now.replace(hour=next_hour, minute=next_block, second=0, microsecond=0)
    return next_time

next_time = get_safe_batch_time()

time_data = {
    "next_time": next_time.strftime("%Y-%m-%d %H:%M:%S"),
    "hour": next_time.strftime("%H"),
    "minute": next_time.strftime("%M")
}

# JSON 파일에 저장
with open("batch_time.json", "w", encoding="utf-8") as f:
    json.dump(time_data, f, ensure_ascii=False, indent=2)

print("✅ 저장 완료:", time_data)

# 필요 시 문자열도 바로 사용
hour_str = next_time.strftime("%H")
minute_str = next_time.strftime("%M")

# 개별 내역 출고 
def test_stock_outflow(page):
    try:
        bay_login(page, "admin")
        page.goto(URLS["bay_rules"])
        page.wait_for_selector("data-testid=btn_edit", timeout=10000)

        # 출고 직전 가장 가까운 시간으로 발주 규칙 변경(자동화규칙_개별, 자동화규칙_묶음)
        for rule in order_rules:
            page.locator("data-testid=input_search").fill(rule)
            page.wait_for_timeout(1000)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            page.locator("data-testid=btn_edit").click()
            page.wait_for_timeout(2000) 

            # ⏰ 시간 설정
            current_hour = page.locator("data-testid=drop_hour_trigger").text_content()
            if current_hour != hour_str:
                page.locator("data-testid=drop_hour_trigger").click()
                page.wait_for_timeout(1000)
                page.locator(f'div[data-value="{hour_str}"]').click()
                page.wait_for_timeout(1000)

            # ⏱️ 분 설정
            current_minute = page.locator("data-testid=drop_minute_trigger").text_content()
            if current_minute != minute_str:
                page.locator("data-testid=drop_minute_trigger").click()
                page.wait_for_timeout(1000)
                page.locator(f'div[data-value="{minute_str}"]').click()
                page.wait_for_timeout(1000)
            
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=txt_title")).to_have_text("발주 규칙 변경 제품", timeout=3000)
            page.wait_for_timeout(1000)
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=toast_edit_pending")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)
        
        # 출고 처리
        bay_login(page, "jekwon")
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(2000)
        stock_manager = StockManager(page)

        for product in products:
            stock_manager.product_name = product
            stock_manager.search_product_by_name(product)

            current_stock = stock_manager.get_current_stock()

            # 출고 수량 계산
            outflow_qty = current_stock

            # 출고 처리
            stock_manager.perform_outflow(outflow_qty)

            updated = stock_manager.get_current_stock()
            expected = current_stock - outflow_qty
            assert updated == expected, f"[FAIL] {product} 출고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 출고 확인: {product} → {updated}")

            ordered_product.append(product)

           
    except Exception as e:
        print(f"❌ 출고 테스트 실패: {str(e)}")
        raise

# 재고 리스트에서 출고 
def test_edit_stocklist_and_auto_order(page):
    bay_login(page, "jekwon")

    stock_manager = StockManager(page)
    txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."
    for product in reject_products:

        # 제품 검색 후 수정 버튼 클릭
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(2000)

        page.locator("data-testid=input_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)

        row = page.locator("table tbody tr").first

        # 현재 재고(6열) 값 가져오기
        cell_6 = row.locator("td").nth(5)
        value_6 = int(cell_6.inner_text().strip())

        # (출고이력)8열 값 가져오기
        cell_8 = row.locator("td").nth(7)
        value_8 = int(cell_8.inner_text().strip())

        page.locator("data-testid=btn_edit").first.click()
        page.wait_for_timeout(1000)

        # 8번째 셀(출고)의 input에 출고량 입력
        sum_value = value_6 + value_8
        input_field = row.locator("td").nth(7).locator("input")
        input_field.scroll_into_view_if_needed()
        input_field.fill(str(sum_value))
        page.wait_for_timeout(1000)

        # 저장 버튼 클릭 후 토스트 확인
        page.locator("data-testid=btn_edit_bulk").click()
        expect(page.locator("data-testid=toast_outflow")).to_have_text(txt_outflow, timeout=10000)
        page.wait_for_timeout(1000)

        ordered_product.append(product)

    
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    for product in ordered_product:
        # 발주 예정 페이지에서 확인
        check_order_pending_history(page, "자동화규칙_개별", product, "승인 요청", manual=False, group=False)
        # # 승인 요청 페이지에서 확인
        # check_approval_history(page, "승인 대기", product)

# 통합내역을 위한 출고 
def test_outflow_for_batch_order(page):
    bay_login(page, "jekwon")
    # 출고 처리 
    txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_timeout(2000)
    product_list = [f"배치 확인 제품 {i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성

    product_list.extend(["발주 거절 제품 3", "발주 삭제 제품 1"])

    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(300)
        page.get_by_role("option", name="출고", exact=True).click()
        page.wait_for_timeout(300)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(300)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(300)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(300)
        # 현재 재고 텍스트 가져오기
        stock_text = page.locator('[data-testid="txt_current_stock"]').last.text_content()
        # 쉼표 제거하고 숫자로 변환
        current_stock = int(stock_text.replace(",", "").strip())
        # 출고량 = 현 재고수량 
        outflow_qty = current_stock

        page.locator("data-testid=input_qty").last.fill(str(outflow_qty))
        page.wait_for_timeout(300)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 출고")
        page.wait_for_timeout(300)

        if idx < len(product_list) - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)
                page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_outflow")).to_have_text(txt_outflow, timeout=10000)
    page.wait_for_timeout(1000)
    # 발주 내역 미노출 확인 
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)

    today_btn_id = datetime.now().strftime("btn_day_%m%d")  # 예: btn_day_0710
    
    page.locator("[data-testid=select_startday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)
    
    page.locator("[data-testid=select_endday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)

    expect(page.locator("data-testid=drop_status_trigger")).to_be_visible(timeout=8000)
    page.locator("data-testid=drop_status_trigger").click()
    expect(page.locator("data-testid=drop_status_item")).to_be_visible(timeout=5000)
    page.locator('[role="option"]').filter(has_text="발주 요청").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill("배치 확인 제품 3")
    page.wait_for_timeout(500)

    page.locator("[data-testid=btn_search]").click()
    page.wait_for_timeout(2000)

    expect(page.locator("data-testid=history")).not_to_be_visible(timeout=5000)

    # 발주 예정 내역 노출 확인 
    page.goto(URLS["bay_order_pending"])
    page.wait_for_selector("data-testid=input_search", timeout=5000)

    for idx, product in enumerate(product_list, start=1):
        if idx in (3, 6, 9): 
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, True)
        elif idx == 10: # 발주 거절 제품 1
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, False)
        elif idx == 11: # 발주 삭제 제품 1
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, True)
        else:
            continue
        page.wait_for_timeout(3000)
    