import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status_by_order_id, get_order_id_from_order_list, filter_products_by_delivery_status
from helpers.save_test_result import save_test_result  
from playwright.sync_api import Page

def test_order_status_cancel(page: Page):
    status_name = "발주 취소"
    expected = order_status_map["발주 취소"]
    
    try:
        # 제품명 필터링 및 랜덤 선택 후 order_id 가져오기
        filtered_products = filter_products_by_delivery_status(6)  # 필터링된 제품
        if not filtered_products:
            raise ValueError(f"[FAIL] '발주 취소' 상태의 제품이 없습니다.")

        product = random.choice(filtered_products)
        product_name = product["kor"]
        order_id = get_order_id_from_order_list(page, product_name)
        
        if not order_id:
            raise ValueError(f"[FAIL] 발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.")

        # 상태 확인
        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        error_message = f"❌ Error in test_order_status_cancel: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        save_test_result("test_order_status_cancel", error_message, status="FAIL")
        raise  # Reraise the exception to maintain test flow
