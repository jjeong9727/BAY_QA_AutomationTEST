import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

# def get_filtered_products(stock_manager, page):
    # 서버와 동기화
    # valid_products = sync_product_names_with_server(page)

    # # 필터링
    # return [
    #     p for p in valid_products
    #     if p.get("stock_qty", 0) <= p.get("safety_stock", 0)
    #     and p.get("order_flag", 1) == 0
    # ]

# def get_have_stock_product(stock_manager, page):
#     # 전체 상품 목록 가져오기
#     all_products = stock_manager.load_product_from_json()

#     # 조건에 맞는 상품 필터링
#     filtered_products = [
#         p for p in all_products
#         if p.get("stock_qty", 0) >= 1 and p.get("order_flag", 1) == 0
#     ]

#     if not filtered_products:
#         raise ValueError("조건에 맞는 상품이 없습니다.")

#     # 랜덤으로 하나 선택
#     product = random.choice(filtered_products)
#     return product
products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3", "발주 거절 제품 1", "발주 거절 제품 2"]
def test_stock_inflow(page):
    try:
        bay_login(page)

        stock_manager = StockManager(page)

        # # 3개 제품을 랜덤으로 선택하여 입고 테스트 진행
        # filtered_products = stock_manager.load_product_from_json()

        if len(products) < 3:
            raise AssertionError(f"❌ 조건에 맞는 제품이 {len(products)}개만 존재합니다. 3개 이상이 필요합니다.")

        # # 조건에 맞는 제품들 중에서 3개를 랜덤으로 선택
        # selected_products = random.sample(products, 3)

        

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