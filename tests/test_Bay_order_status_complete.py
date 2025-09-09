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
alim_talk_product = "수동 발주 제품 3"

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
# 발주 진행 상태에서 수령 확정 (운송장 X)
def test_order_status_complete_bf(page: Page):
    run_order_status_check(page, delivery_status=7, product_name=filtered_products[1])
    
# 배송 진행 상태에서 수령 확정 (운송장 O)
def test_order_status_complete_af(page: Page):
    run_order_status_check(page, delivery_status=4, product_name=filtered_products[0])

# 재발송 버튼 확인
def test_resend_alimtalk(page:Page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_orderList"])
    page.wait_for_selector("data-testid=input_search", timeout=5000)
    search_order_history(page, alim_talk_product, "발주 요청")

    for i in range(1, 6):  # 1~5회 시도
        page.wait_for_selector("data-testid=btn_resend", timeout=5000)
        page.locator("data-testid=btn_resend").first.click()

        expect(page.locator("data-testid=txt_resend")).to_have_text("재발송하시겠습니까?", timeout=5000)
        page.locator("data-testid=btn_confirm").click()

        if i <= 3:
            # 1~3회차 → 정상 재발송 완료 토스트
            expect(page.locator("data-testid=toast_resend")).to_have_text("재발송이 완료되었습니다.", timeout=5000)
            print(f"✅ {i}회차: 재발송 성공")
        else:
            # 4회차 이후 → 최대 횟수 초과 토스트
            expect(page.locator("data-testid=toast_resend_max")).to_have_text("재발송은 최대 3회까지만 가능합니다.", timeout=5000)
            print(f"⚠️ {i}회차: 재발송 최대 횟수 초과")