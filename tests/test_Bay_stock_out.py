import random
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
def test_stock_outflow(page):
    try:
        bay_login(page)

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
            max_outflow = current_stock - 1
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

def test_edit_stockList_and_auto_order(page):
    bay_login(page)

    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()

    # 1개 제품을 랜덤으로 선택하여 출고 테스트 진행
    filtered_products = get_filtered_products(stock_manager)
    if len(filtered_products) < 1:
        print(f"❌ 조건에 맞는 제품이 없습니다.")
        return

    # 조건에 맞는 제품들 중에서 1개를 랜덤으로 선택
    product = random.sample(filtered_products, 1)
    current_stock = product["stock_qty"]
    outflow = current_stock -1
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)

    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_edit").first.click()
    page.wait_for_timeout(1000)
    row = page.locator("table tbody tr").first
    input_field = row.locator("td").nth(7).locator("input")
    input_field.scroll_into_view_if_needed()
    input_field.fill(str(outflow))
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").first.click()
    expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    expect(page.locator("data-testid=txt_date")).to_be_visible(timeout=3000)

def test_edit_product_and_auto_order(page):
    bay_login(page)
    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()

    # 1개 제품을 랜덤으로 선택하여 출고 테스트 진행
    filtered_products = get_filtered_products(stock_manager)
    if len(filtered_products) < 1:
        print(f"❌ 조건에 맞는 제품이 없습니다.")
        return

    # 조건에 맞는 제품들 중에서 1개를 랜덤으로 선택
    product = random.sample(filtered_products, 1)
    current_stock = product["stock_qty"]
    safety = current_stock + 10

    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    for i in range(row_count):
        edit_button = rows.nth(i).locator("td:nth-child(11) >> text=수정")
        if edit_button.is_visible():
            print(f"✅ {i}번째 행의 수정 버튼 클릭")
            edit_button.click()
            page.wait_for_timeout(1000)
            break

    txt_order = "자동 발주를 진행하시겠습니까?"
    page.locator("data-testid=input_stk_safe").fill(safety)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_order")).to_have_text(txt_order, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_search").fill(product)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_date")).to_be_visible(timeout=3000)







    