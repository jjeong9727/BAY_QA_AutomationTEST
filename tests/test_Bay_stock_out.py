import random
import time
from datetime import datetime
from playwright.sync_api import TimeoutError, expect
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag
from helpers.common_utils import bay_login
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

    if minute >= 28:
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
        current_hour = page.locator('[data-testid="drop_hour_trigger"]').text_content()
        if current_hour != hour_str:
            page.locator('[data-testid="drop_hour_trigger"]').click()
            page.locator('[data-testid="drop_hour_search"]').fill(hour_str)
            page.locator('[data-testid="drop_hour_item"]', has_text=hour_str).click()

        # ⏱️ 분 설정
        current_minute = page.locator('[data-testid="drop_minute_trigger"]').text_content()
        if current_minute != minute_str:
            page.locator('[data-testid="drop_minute_trigger"]').click()
            page.locator('[data-testid="drop_minute_search"]').fill(minute_str)
            page.locator('[data-testid="drop_minute_item"]', has_text=minute_str).click()
        
        page.locator("data-testid=btn_confirm").click()

        expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        # 출고 처리
        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 1개 제품을 랜덤으로 선택하여 출고 테스트 진행
        filtered_products = get_filtered_products(stock_manager)
        if len(filtered_products) < 1:
            print(f"❌ 조건에 맞는 제품이 없습니다.")
            return

        # 조건에 맞는 제품들 중에서 1개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 1)

        for product in selected_products:
            stock_manager.product_name = product['kor']
            stock_manager.search_product_by_name(product['kor'])

            current_stock = stock_manager.get_current_stock()
            safety_stock = product.get('safety_stock', 0)

            # 출고 수량 계산
            max_outflow = current_stock 
            calculated_outflow = current_stock - safety_stock
            outflow_qty = max(1, min(max_outflow, calculated_outflow))

            # 출고 처리
            stock_manager.perform_outflow(outflow_qty)

            updated = stock_manager.get_current_stock()
            expected = current_stock - outflow_qty
            assert updated == expected, f"[FAIL] {product['kor']} 출고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 출고 확인: {product['kor']} → {updated}")

           # 발주 내역 페이지 이동
            page.goto(URLS["bay_orderList"])
            expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)

            # 제품명 검색
            page.fill("data-testid=input_search", stock_manager.product_name)
            page.wait_for_timeout(1000)
            page.click("data-testid=btn_search")
            page.wait_for_timeout(5000)

            # history 항목이 하나 이상 있는지 확인 (strict 모드 회피)
            history_div = page.locator("div[data-testid=history]")
            count = history_div.count()

            if count == 0:
                raise AssertionError("❌ history 항목이 존재하지 않습니다.")
            else:
                print(f"[INFO] {count}개의 history 항목이 확인되었습니다.")

            # 모든 history 항목을 순차적으로 확인
            history_items = history_div.all()
            product_name_to_search = stock_manager.product_name
            found_product = False

            # 각 history 항목을 순차적으로 확인
            for history in history_items:
                # 첫 번째 테이블에서 2열에 제품명이 있는지 확인
                first_row_product_name = history.locator("table tbody tr:first-child td:nth-child(2)").inner_text()

                if product_name_to_search in first_row_product_name:
                    found_product = True
                    print(f"[PASS] {product_name_to_search}의 발주 내역을 찾았습니다.")
                    break

            # 모든 history 항목을 확인한 후에도 제품을 찾지 못했다면 FAIL 처리
            if not found_product:
                raise AssertionError(f"[FAIL] {product_name_to_search}의 발주 내역을 찾을 수 없습니다.")

            # 출고 후 재고 값을 json에 저장
            update_product_flag(product['kor'], stock_qty=expected, order_flag=1, delivery_status=1)

    except Exception as e:
        print(f"❌ 출고 테스트 실패: {str(e)}")
        raise

def test_edit_stocklist_and_auto_order(page):
    bay_login(page)

    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()

    # 조건에 맞는 제품 필터링
    filtered_products = get_filtered_products(stock_manager)
    if len(filtered_products) < 2:
        print("❌ 조건에 맞는 제품이 2개 이상 없습니다.")
        return

    # 2개 제품 랜덤 선택
    selected_products = random.sample(filtered_products, 2)

    for product in selected_products:
        current_stock = product["stock_qty"]
        outflow = 1
        expected = current_stock - outflow
        txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."

        # 제품 검색 후 편집 버튼 클릭
        page.goto(URLS["bay_stockList"])
        page.wait_for_timeout(2000)

        page.locator("data-testid=input_search").fill(product["kor"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_edit").first.click()
        page.wait_for_timeout(1000)

        # 7번째 셀의 input에 출고량 입력
        row = page.locator("table tbody tr").first
        input_field = row.locator("td").nth(7).locator("input")
        input_field.scroll_into_view_if_needed()
        input_field.fill(str(outflow))
        page.wait_for_timeout(1000)

        # 저장 버튼 클릭 후 토스트 확인
        page.locator("data-testid=btn_edit").first.click()
        expect(page.locator("data-testid=toast_edit")).to_have_text(txt_outflow, timeout=3000)
        page.wait_for_timeout(1000)

        # 발주 내역 페이지에서 날짜 확인
        wait_until(next_time)
        today = datetime.now().strftime("%Y. %m. %d")
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)

        page.locator("data-testid=input_search").fill(product["kor"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        expect(page.locator("data-testid=txt_date").first).to_have_text(today)

        # 상태 업데이트
        update_product_flag(product["kor"], stock_qty=expected, order_flag=1, delivery_status=1)