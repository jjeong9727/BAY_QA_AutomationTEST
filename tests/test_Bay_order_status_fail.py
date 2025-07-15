import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    check_order_status_by_order_id,
    get_order_id_from_order_list,
    filter_products_by_delivery_status,
    search_order_history
)
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login


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

        bay_login(page)
         
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        page.locator("data-testid=drop_status_trigger").click()
        expect(page.locator("data-testid=drop_status_item")).to_be_visible(timeout=5000)
        page.locator('[role="option"]').filter(has_text="발주 실패").click()
        page.wait_for_timeout(1000)
        # 제품명 입력
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(500)
        # 검색 버튼 클릭
        page.locator("[data-testid=btn_search]").click()
        page.wait_for_timeout(2000)

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
