import random
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag
from helpers.save_test_result import save_test_result  

def get_filtered_products(stock_manager):
    """재고가 안전 재고 이하이고, order_flag가 0인 제품만 선택"""
    products = stock_manager.get_all_product_names()
    return [p for p in products if p.get("stock_qty", 0) <= p.get("safety_stock", 0) and p.get("order_flag", 1) == 0]

def test_stock_inflow(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])

        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 3개 제품을 랜덤으로 선택하여 입고 테스트 진행
        filtered_products = get_filtered_products(stock_manager)

        if len(filtered_products) < 3:
            print("❌ 조건에 맞는 제품이 3개 미만입니다.")
            save_test_result("test_stock_inflow", "조건에 맞는 제품이 3개 미만입니다.", status="FAIL")
            return

        selected_products = random.sample(filtered_products, 3)

        for product in selected_products:
            stock_manager.search_product_by_name(product['kor'])

            inflow_qty = random.randint(6, 10)  # 랜덤 입고 수량
            stock_manager.perform_inflow(inflow_qty)

            updated = stock_manager.get_current_stock()
            expected = stock_manager.initial_stock + inflow_qty
            assert updated == expected, f"[FAIL] {product['kor']} 입고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 입고 확인: {product['kor']} → {updated}")

            # 입고 후 재고 값을 json 파일에 저장
            update_product_flag(product['kor'], stock=expected)

        save_test_result("test_stock_inflow", f"[PASS] 입고 테스트 완료", status="PASS")

    except Exception as e:
        print(f"❌ 입고 테스트 실패: {str(e)}")
        save_test_result("test_stock_inflow", f"[FAIL] 입고 테스트 실패: {str(e)}", status="FAIL")
        raise
