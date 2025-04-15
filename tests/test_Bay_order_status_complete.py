import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id
)
from playwright.sync_api import Page
from config import URLS, Account


def run_order_status_check(page: Page, delivery_status: int, expected_key: str):
    status_name = "수령 완료"
    expected = order_status_map[expected_key]

    try:
        filtered_products = filter_products_by_delivery_status(delivery_status)
        if not filtered_products:
            raise ValueError(f"'수령 완료' 상태의 제품이 없습니다.")

        product = random.choice(filtered_products)
        product_name = product["kor"]

        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login", timeout=50000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"[발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.")

        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        print(f"❌ Error in test_order_status_complete: {str(e)}")
        raise


def test_order_status_complete_bf(page: Page):
    run_order_status_check(page, delivery_status=7, expected_key="수령 완료(배송전)")


def test_order_status_complete_af(page: Page):
    run_order_status_check(page, delivery_status=4, expected_key="수령 완료(배송후)")
