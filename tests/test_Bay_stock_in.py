import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

# def get_filtered_products(stock_manager, page):

products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3", "발주 거절 제품 1", "발주 거절 제품 2"]
def test_stock_inflow(page):
    try:
        bay_login(page)
        stock_manager = StockManager(page)
        if len(products) < 3:
            raise AssertionError(f"❌ 조건에 맞는 제품이 {len(products)}개만 존재합니다. 3개 이상이 필요합니다.")

        for product in products:
            print(product)
            stock_manager.product_name = product  # 제품명을 클래스 속성에 저장
            stock_manager.search_product_by_name(product)

            inflow_qty = random.randint(6, 10)  # 랜덤 입고 수량
            stock_manager.perform_inflow(inflow_qty)  

            updated = stock_manager.get_current_stock()
            expected = stock_manager.initial_stock + inflow_qty
            assert updated == expected, f"[FAIL] {product} 입고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 입고 확인: {product} → {updated}")

            # # 입고 후 재고 값을 json 파일에 저장
            # update_product_flag(product, stock_qty=expected)

    except Exception as e:
        print(f"❌ 입고 테스트 실패: {str(e)}")
        raise