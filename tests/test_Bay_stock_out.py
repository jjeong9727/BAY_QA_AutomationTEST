from __future__ import annotations
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

# 배치 시간 계산 후 JSON에 저장
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

def test_stock_outflow(page):
    try:
        bay_login(page, "jekwon")
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
