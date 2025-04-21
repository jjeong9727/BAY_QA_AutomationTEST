import random
from playwright.sync_api import TimeoutError
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag

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
def test_stock_outflow(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])

        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 3개 제품을 랜덤으로 선택하여 출고 테스트 진행
        filtered_products = get_filtered_products(stock_manager)

    

        if len(filtered_products) < 3:
            print(f"❌ 조건에 맞는 제품이 {len(filtered_products)}개만 존재합니다. 3개 이상이 필요합니다.")
            return

        # 조건에 맞는 제품들 중에서 3개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 3)

        # 랜덤 선택된 제품 출력 (디버깅용)


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
            page.wait_for_timeout(1000)

            # 제품명 검색
            page.fill("data-testid=input_search", stock_manager.product_name)
            page.wait_for_timeout(500)
            page.click("data-testid=btn_search")

            # history 항목이 나타날 때까지 대기
            try:
                page.wait_for_selector("data-testid=history", timeout=5000)
            except TimeoutError:
                print("🔁 history 항목이 안 보여서 페이지 새로고침 후 재시도합니다.")
                page.reload()
                page.fill("data-testid=input_search", stock_manager.product_name)
                page.wait_for_timeout(300)
                page.click("data-testid=btn_search")
                page.wait_for_selector("data-testid=history", timeout=5000)  # 마지막 시도

                
            # 모든 history 항목을 순차적으로 확인
            history_items = page.locator("data-testid=history").all()  # 모든 history 항목 가져오기
            product_name_to_search = stock_manager.product_name
            found_product = False  # 제품을 찾았는지 여부를 추적

            # 각 history 항목을 순차적으로 확인
            for history in history_items:
                # 첫 번째 테이블에서 2열에 제품명이 있는지 확인
                first_row_product_name = history.locator("table tbody tr:first-child td:nth-child(2)").inner_text()

                # 제품명이 첫 번째 항목의 2열에 있는지 확인
                if product_name_to_search in first_row_product_name:
                    found_product = True  # 제품을 찾았으므로 found_product를 True로 설정
                    print(f"[PASS] {product_name_to_search}의 발주 내역을 찾았습니다.")
                    break  # 찾았으면 더 이상 확인할 필요 없음

            # 모든 history 항목을 확인한 후에도 제품을 찾지 못했다면 FAIL 처리
            if not found_product:
                raise AssertionError(f"[FAIL] {product_name_to_search}의 발주 내역을 찾을 수 없습니다.")

            # 출고 후 재고 값을 json에 저장
            update_product_flag(product['kor'], stock_qty=expected, order_flag=1, delivery_status=1)

    except Exception as e:
        print(f"❌ 출고 테스트 실패: {str(e)}")
        raise
