import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id, search_order_history
)
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
from config import URLS, Account
filtered_products = ["자동화개별제품_2", "자동화개별제품_3"] 

def run_order_status_check(page: Page, delivery_status: int, product_name:str):
    status_name = "수령 완료"
    
    # 상태에 따른 expected 키 매핑
    status_key_map = {
        7: "수령 완료(배송전)", # 제품_3
        4: "수령 완료(배송후)", # 제품_2
    }

    expected_key = status_key_map.get(delivery_status)
    if not expected_key:
        raise ValueError(f"지원하지 않는 delivery_status: {delivery_status}")

    expected = order_status_map[expected_key]

    try:
        
        bay_login(page, "jekwon")

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        search_order_history(page, product_name, status_name)

        # order_id 확인 및 상태 체크
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"[발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.]")

        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        print(f"❌ Error in test_order_status_complete: {str(e)}")
        raise



def test_order_status_complete_bf(page: Page):
    run_order_status_check(page, delivery_status=7, product_name=filtered_products[1])
    
    

def test_order_status_complete_af(page: Page):
    run_order_status_check(page, delivery_status=4, product_name=filtered_products[0])

