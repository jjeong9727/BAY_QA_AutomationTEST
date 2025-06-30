import random
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login




def get_filtered_products(stock_manager, page):
    """
    재고가 안전 재고 이하이고, order_flag가 0인 제품만 선택
    """
    # 서버와 동기화
    valid_products = sync_product_names_with_server(page)

    # 필터링
    return [
        p for p in valid_products
        if p.get("stock_qty", 0) <= p.get("safety_stock", 0)
        and p.get("order_flag", 1) == 0
    ]


def test_stock_inflow(page):
    try:
        bay_login(page)
        

        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 3개 제품을 랜덤으로 선택하여 입고 테스트 진행
        filtered_products = get_filtered_products(stock_manager, page)

        if len(filtered_products) < 3:
            print(f"❌ 조건에 맞는 제품이 {len(filtered_products)}개만 존재합니다. 3개 이상이 필요합니다.")
            return

        # 조건에 맞는 제품들 중에서 3개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 3)

        print("[선택된 제품]", [p["kor"] for p in selected_products])


        for product in selected_products:
            print(product)
            stock_manager.product_name = product['kor']  # 제품명을 클래스 속성에 저장
            stock_manager.search_product_by_name(product['kor'])

            inflow_qty = random.randint(6, 10)  # 랜덤 입고 수량
            stock_manager.perform_inflow(inflow_qty)  # 이제 두 번째 인자 없이 호출

            updated = stock_manager.get_current_stock()
            expected = stock_manager.initial_stock + inflow_qty
            assert updated == expected, f"[FAIL] {product['kor']} 입고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 입고 확인: {product['kor']} → {updated}")

            # 입고 후 재고 값을 json 파일에 저장
            update_product_flag(product['kor'], stock_qty=expected)


    except Exception as e:
        print(f"❌ 입고 테스트 실패: {str(e)}")
        raise
