import random
import re
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.order_status_utils import search_order_history
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
import time

def get_safe_batch_time() -> datetime:
    now = datetime.now()
    minute = now.minute
    base_minute = (minute // 10) * 10

    if minute >= 28: # 테스트 해보고 시간 조정 필요할수도?
        # 다다음 배치
        next_minute = base_minute + 20
    else:
        # 다음 배치
        next_minute = base_minute + 10

    # 시(hour) 넘어가는 경우 처리
    if next_minute >= 60:
        next_hour = now.hour + 1
        next_time = now.replace(hour=next_hour % 24, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(minute=next_minute, second=0, microsecond=0)

    return next_time

def wait_until(target_time: datetime):
    print(f"⏳ 다음 발주 배치 시각까지 대기 중: {target_time.strftime('%H:%M')}")
    while True:
        now = datetime.now()
        remaining = (target_time - now).total_seconds()
        if remaining <= 0:
            print("✅ 도달 완료! 발주 내역 확인 시작")
            break
        elif remaining > 60:
            print(f"🕒 {int(remaining)}초 남음... 60초 대기")
            time.sleep(60)
        else:
            print(f"🕒 {int(remaining)}초 남음... {int(remaining)}초 대기")
            time.sleep(remaining)

def test_inflow (page:Page):
    bay_login(page)
    page.goto(URLS["bay_stockadd"])
    page.wait_for_timeout(2000)
    txt_inflow = "9개의 재고 입고가 완료되었습니다."
    product_list = [f"자동화제품_{i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성
    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="입고", exact=True).click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)
        
        # 입고량 계산 
        inflow_qty = 10

        page.locator("data-testid=input_qty").last.fill(str(inflow_qty))
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 입고")
        page.wait_for_timeout(1000)

        if idx < len(product_list) - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    # expect(page.locator("data-testid=toast_inflow")).to_have_text(txt_inflow, timeout=10000)
    page.wait_for_timeout(2000)

def test_outflow(page:Page):
    bay_login(page)
    # 출고 직전 가장 가까운 시간으로 발주 규칙 변경 (자동화규칙_묶음)
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_search").fill("자동화규칙_묶음")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").click()
    page.wait_for_timeout(2000)

    next_time = get_safe_batch_time()
    hour_str = next_time.strftime("%H")  
    minute_str = next_time.strftime("%M")  

    # ⏰ 시간 설정
    current_hour = page.locator("data-testid=drop_hour_trigger").text_content()
    if current_hour != hour_str:
        page.locator("data-testid=drop_hour_trigger").click()
        page.wait_for_timeout(1000)
        page.locator(f'div[data-testid^="drop_hour_item_"][data-value="{hour_str}"]').click()
        page.wait_for_timeout(1000)

    # ⏱️ 분 설정
    current_minute = page.locator("data-testid=drop_minute_trigger").text_content()
    if current_minute != minute_str:
        page.locator("data-testid=drop_minute_trigger").click()
        page.wait_for_timeout(1000)
        page.locator(f'div[data-testid^="drop_minute_item_"][data-value="{minute_str}"]').click()
        page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=txt_title")).to_have_text("발주 규칙 변경 제품", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit_pending")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    
    # 출고 처리
    txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_timeout(2000)
    product_list = [f"자동화제품_{i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성

    stock_manager = StockManager(page)

    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="출고", exact=True).click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)
        # 현재 재고 텍스트 가져오기
        stock_text = page.locator('[data-testid="txt_current_stock"]').last.text_content()
        # 쉼표 제거하고 숫자로 변환
        current_stock = int(stock_text.replace(",", "").strip())
        # 출고량 = 현 재고수량 
        outflow_qty = current_stock

        page.locator("data-testid=input_qty").last.fill(str(outflow_qty))
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 출고")
        page.wait_for_timeout(1000)

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

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)

    today_btn_id = datetime.now().strftime("btn_day_%m%d")  # 예: btn_day_0710
    # 시작일 선택
    page.locator("[data-testid=select_startday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)
    # 종료일 선택
    page.locator("[data-testid=select_endday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)
    # 상태 선택
    expect(page.locator("data-testid=drop_status_trigger")).to_be_visible(timeout=8000)
    page.locator("data-testid=drop_status_trigger").click()
    expect(page.locator("data-testid=drop_status_item")).to_be_visible(timeout=5000)
    page.locator('[role="option"]').filter(has_text="발주 요청").click()
    page.wait_for_timeout(1000)
    # 제품명 입력
    page.locator("data-testid=input_search").fill("자동화제품_3")
    page.wait_for_timeout(500)
    # 검색 버튼 클릭
    page.locator("[data-testid=btn_search]").click()
    page.wait_for_timeout(2000)

    expect(page.locator("data-testid=history")).not_to_be_visible(timeout=5000)

    wait_until(next_time)
    
    page.wait_for_timeout(300000) # 혹시 모를 Delay를 위한 30초 추가 대기

    page.reload()
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)

    page.goto(URLS["bay_orderList"])# 동작 확인후 삭제 필요
    # 대표내역 + 상세 내역 제품명 확인 
    products = ["자동화제품_1", "자동화제품_2", "자동화제품_3"]
    search_order_history(page, "자동화제품_3", "발주 요청")
    rows = page.locator('table tbody tr')
    product_cell = rows.nth(0).locator('td:nth-child(2)')
    product_text = product_cell.inner_text()
    main_product_name = re.split(r"\s*외\s*", product_text)[0].strip()
    print(f"대표 제품명: {repr(main_product_name)}")
    assert main_product_name in products, f"❌ 대표 제품명이 products 리스트에 없음: {main_product_name}"

    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)


    products = ["자동화제품_4", "자동화제품_5", "자동화제품_6"]
    search_order_history(page, "자동화제품_6", "발주 요청")
    rows = page.locator('table tbody tr')
    product_cell = rows.nth(0).locator('td:nth-child(2)')
    product_text = product_cell.inner_text()
    main_product_name = re.split(r"\s*외\s*", product_text)[0].strip()
    print(f"대표 제품명: {repr(main_product_name)}")
    assert main_product_name in products, f"❌ 대표 제품명이 products 리스트에 없음: {main_product_name}"
    
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)


    products = ["자동화제품_7", "자동화제품_8", "자동화제품_9"]
    search_order_history(page, "자동화제품_9", "발주 요청")
    rows = page.locator('table tbody tr')
    product_cell = rows.nth(0).locator('td:nth-child(2)')
    product_text = product_cell.inner_text()
    main_product_name = re.split(r"\s*외\s*", product_text)[0].strip()
    print(f"대표 제품명: {repr(main_product_name)}")
    assert main_product_name in products, f"❌ 대표 제품명이 products 리스트에 없음: {main_product_name}"
    page.wait_for_timeout(1000) 
