import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    check_order_status_by_order_id,
    get_order_id_from_order_list,
    filter_products_by_delivery_status
)
from playwright.sync_api import Page
from config import URLS, Account


def test_order_status_fail(page: Page):
    status_name = "발주 실패"
    expected = order_status_map[status_name]

    try:
        # delivery_status == 6인 제품 목록 필터링
        filtered_products = filter_products_by_delivery_status(6)
        if not filtered_products:
            raise ValueError(f"[FAIL] '{status_name}' 상태의 제품이 없습니다.")

        # 무작위 제품 선택
        product = random.choice(filtered_products)
        product_name = product["kor"]

        # 로그인 및 페이지 이동
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login", timeout=50000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # order_id 가져오기
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"[FAIL] 발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.")

        # 상태 확인
        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        error_message = f"❌ Error in test_order_status_fail: {str(e)}"
        print(error_message)
        raise  # 예외 재전파로 테스트 실패 처리
