import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id
)
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
from config import URLS, Account


def run_order_status_check(page: Page, delivery_status: int):
    status_name = "수령 확정"
    
    # 상태에 따른 expected 키 매핑
    status_key_map = {
        7: "수령 완료(배송전)",
        4: "수령 완료(배송후)",
    }

    expected_key = status_key_map.get(delivery_status)
    if not expected_key:
        raise ValueError(f"지원하지 않는 delivery_status: {delivery_status}")

    expected = order_status_map[expected_key]

    try:
        filtered_products = filter_products_by_delivery_status(delivery_status)
        if not filtered_products:
            raise ValueError(f"'{expected_key}' 상태의 제품이 없습니다.")

        product = random.choice(filtered_products)
        product_name = product["kor"]

        bay_login(page)

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # order_id 확인 및 상태 체크
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"[발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.]")

        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        print(f"❌ Error in test_order_status_complete: {str(e)}")
        raise



def test_order_status_complete_bf(page: Page):
    run_order_status_check(page, delivery_status=7)

def test_order_status_complete_af(page: Page):
    run_order_status_check(page, delivery_status=4)

