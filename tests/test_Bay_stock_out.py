import random
import time
from datetime import datetime
from playwright.sync_api import TimeoutError, expect
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag
from helpers.common_utils import bay_login
from helpers.order_status_utils import search_order_history

ordered_product = []
def get_filtered_products(stock_manager):
    """출고 대상 제품 선정: 재고가 안전 재고 이상이고, order_flag가 0인 제품만 선택"""
    products = stock_manager.get_all_product_names()
    filtered_products = [
        p for p in products
        if p.get("stock_qty", 0) >= p.get("safety", 0) and p.get("order_flag", 1) == 0
    ]
    
    # 필터링된 제품 출력 (디버깅용)
    for product in filtered_products:
        print(f"❓ 필터링된 제품 - 이름: {product['kor']}, 재고: {product['stock_qty']}, 안전 재고: {product['safety']}")
    
    return filtered_products

def get_safe_batch_time() -> datetime:
    now = datetime.now()
    minute = now.minute
    base_minute = (minute // 10) * 10

    # 남은 시간 계산
    minutes_until_next = (base_minute + 10) - minute
    if minutes_until_next <= 3: # 3분 이내면 다다음 배치로 설정
        next_minute = base_minute + 20
    else:
        next_minute = base_minute + 10 # 아니면 다음 배치

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
            print("✅ 도달 완료!")
            time.sleep(60) # 60초 추가 대기
            break
        elif remaining > 60:
            print(f"🕒 {int(remaining)}초 남음... 60초 대기")
            time.sleep(60)
        else:
            print(f"🕒 {int(remaining)}초 남음... {int(remaining)}초 대기")
            time.sleep(remaining)
next_time = get_safe_batch_time()
hour_str = next_time.strftime("%H")  
minute_str = next_time.strftime("%M") 


def test_stock_outflow(page):
    try:
        bay_login(page)
        # 출고 직전 가장 가까운 시간으로 발주 규칙 변경(자동화규칙_개별)
        page.goto(URLS["bay_rules"])
        page.wait_for_timeout(2000)
        page.locator("data-testid=input_search").fill("자동화규칙_개별")
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_edit").click()
        page.wait_for_timeout(2000) 

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
        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 1개 제품을 랜덤으로 선택하여 출고 테스트 진행
        filtered_products = get_filtered_products(stock_manager)
        if len(filtered_products) < 1:
            raise AssertionError("❌ 조건에 맞는 제품이 없습니다.")

        # 조건에 맞는 제품들 중에서 1개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 1)

        for product in selected_products:
            stock_manager.product_name = product['kor']
            stock_manager.search_product_by_name(product['kor'])

            current_stock = stock_manager.get_current_stock()
            safety_stock = product.get('safety_stock', 0)

            # 출고 수량 계산
            outflow_qty = current_stock

            # 출고 처리
            stock_manager.perform_outflow(outflow_qty)

            updated = stock_manager.get_current_stock()
            expected = current_stock - outflow_qty
            assert updated == expected, f"[FAIL] {product['kor']} 출고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 출고 확인: {product['kor']} → {updated}")

            # 출고 후 재고 값을 json에 저장
            update_product_flag(product['kor'], stock_qty=expected, order_flag=1, delivery_status=1)
            ordered_product.append(product['kor'])

    except Exception as e:
        print(f"❌ 출고 테스트 실패: {str(e)}")
        raise

def test_edit_stocklist_and_auto_order(page):
    bay_login(page)

    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()

    ordered_product = []

    # 조건에 맞는 제품 필터링
    filtered_products = get_filtered_products(stock_manager)
    if len(filtered_products) < 2: 
        print("❌ 조건에 맞는 제품이 2개 이상 없습니다.")
        return

    # 2개 제품 랜덤 선택
    selected_products = random.sample(filtered_products, 2)

    for product in selected_products:
        current_stock = product["stock_qty"]
        outflow = current_stock
        expected = current_stock - outflow
        txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."

        # 제품 검색 후 수정 버튼 클릭
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(2000)

        page.locator("data-testid=input_search").fill(product["kor"])
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
        expect(page.locator("data-testid=toast_outflow")).to_have_text(txt_outflow, timeout=3000)
        page.wait_for_timeout(1000)
        ordered_product.append({"kor": product["kor"]} )

    # 발주 내역 페이지에서 날짜 확인
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_search").fill(product["kor"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_resend").is_hidden(timeout=3000)
    wait_until(next_time)
    page.wait_for_timeout(1000) 
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)

    for product in ordered_product:
        search_order_history(page, product["kor"], "발주 요청")
        rows = page.lacator('table tbody tr')
        product_cell = rows.nth(0).locator('td:nth-child(2)')
        product_text = product_cell.inner_text()
        print(f"제품명: {product_text}")
        assert product_text in product["kor"], f"❌ 제품명이 발주 내역에 없음: {product["kor"]}"


        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)
        # 상태 업데이트
        update_product_flag(product, stock_qty=expected, order_flag=1, delivery_status=1)