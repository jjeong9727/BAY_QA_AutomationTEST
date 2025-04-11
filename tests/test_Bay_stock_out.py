import random
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag
from helpers.save_test_result import save_test_result  

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
            save_test_result("test_stock_outflow", f"조건에 맞는 제품이 {len(filtered_products)}개 미만입니다.", status="FAIL")
            return

        # 조건에 맞는 제품들 중에서 3개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 3)

        # 랜덤 선택된 제품 출력 (디버깅용)


        for product in selected_products:
            stock_manager.product_name = product['kor']  # 제품명을 클래스 속성에 저장
            stock_manager.search_product_by_name(product['kor'])

            # 출고 수량 계산: 출고 후 재고가 1 이상이고 안전 재고 이하인 값으로 계산
            current_stock = stock_manager.get_current_stock()
            safety_stock = product.get('safety_stock', 0)
            outflow_qty = current_stock - safety_stock
            outflow_qty = outflow_qty if outflow_qty >= 1 else 1  # 최소 출고 수량 1로 설정

            # 출고 처리
            stock_manager.perform_outflow(outflow_qty)  # 출고 수량만큼 출고

            updated = stock_manager.get_current_stock()
            expected = current_stock - outflow_qty  # 출고 후 재고는 기존 재고에서 출고 수량만큼 차감
            assert updated == expected, f"[FAIL] {product['kor']} 출고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 출고 확인: {product['kor']} → {updated}")

            # 출고 후 재고 값을 json 파일에 저장
            update_product_flag(product['kor'], stock=expected)

            # 발주 내역 화면으로 이동 후 발주 내역 확인
            page.goto(URLS["bay_orderList"])
            page.fill("data-testid=input_search", product['kor'])
            page.locator("data-testid=btn_search").click()
            page.wait_for_selector(f"text={product['kor']}")  # 발주 내역에 제품명이 있어야 함
            assert page.locator(f"text={product['kor']}").is_visible(), f"{product['kor']}의 발주 내역을 찾을 수 없습니다."

        save_test_result("test_stock_outflow", f"[PASS] 출고 테스트 완료", status="PASS")

    except Exception as e:
        print(f"❌ 출고 테스트 실패: {str(e)}")
        save_test_result("test_stock_outflow", f"[FAIL] 출고 테스트 실패: {str(e)}", status="FAIL")
        raise
