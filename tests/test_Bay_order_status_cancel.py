import json
import random
from datetime import datetime, timedelta
import time
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status, search_order_history, get_order_id_from_order_list, check_order_status_by_order_id
)
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login

product_name = "자동화개별제품_1"

def wait_until_batch_ready(json_path="batch_time.json"):
    # JSON 불러오기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # next_time 문자열 → datetime 변환
    next_time = datetime.strptime(data["next_time"], "%Y-%m-%d %H:%M:%S")
    deadline = next_time + timedelta(minutes=1)

    now = datetime.now()
    print(f"⏳ 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📌 배치 기준 시간: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📌 최소 실행 시간: {deadline.strftime('%Y-%m-%d %H:%M:%S')}")

    # deadline(=next_time+1분) 전이면 기다리고, 지나면 바로 실행
    if now < deadline:
        wait_seconds = (deadline - now).total_seconds()
        print(f"⌛ {wait_seconds:.0f}초 대기 후 테스트 시작")
        time.sleep(wait_seconds)

    print("✅ 조건 충족! 테스트를 진행합니다.")
# 발주 취소 확인 
def test_order_cancel(page: Page):
    try:
        # 배치 발주 시간+1분 까지 대기 
        wait_until_batch_ready("batch_time.json")

        bay_login(page, "jekwon")

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        search_order_history(page, product_name, "발주 요청")

        # 검색된 제품의 order_id 값 가져오기
        order_id = get_order_id_from_order_list(page, product_name)
        
        if not order_id:
            raise ValueError(f"Order ID for product {product_name} not found")

        # 취소 버튼
        txt_cancel = "발주를 취소하시겠습니까?"
        page.locator("data-testid=btn_order_cancel").click()  # 취소 버튼 클릭
        expect(page.locator("data-testid=txt_cancel")).to_have_text(txt_cancel, timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()  
        expect(page.locator("data-testid=toast_cancel")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        # 발주 내역에서 해당 제품을 "발주 취소" 상태인지 확인
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                print(f"[PASS] 발주 취소 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # # 발주 진행 상태 확인 후 delivery_status 값을 5로 업데이트 (발주 취소 상태)
        # update_product_status_in_json(product_name=product_name, delivery_status=5, order_flag=0)  # delivery_status를 5로 업데이트 (발주 취소), order_flag=0

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["발주 취소"]  # 발주 취소 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "발주 취소", order_id, expected_status_conditions)

    except Exception as e:
        error_message = f"❌ Error in test_order_cancel: {str(e)}"
        print(error_message)
        raise  # Reraise the exception to maintain test flow

def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False)
        # 발주 수락과 상태 업데이트 작업을 하나의 함수에서 처리
        test_order_cancel(page)
    
        page.close()

if __name__ == "__main__":
    main()


# 발주 실패 확인 
def test_order_status_fail(page: Page):
    status_name = "발주 실패"
    try:
        filtered_products = filter_products_by_delivery_status(6)
        if not filtered_products:
            raise ValueError(f"[FAIL] '{status_name}' 상태의 제품이 없습니다.")

        # 무작위 제품 선택
        product = random.choice(filtered_products)
        product_name = product["kor"]

        bay_login(page, "jekwon")
         
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

        # 상태 확인
        expect(page.locator("[data-testid=btn_receive]")).to_be_disabled(timeout=3000)
        expect(page.locator("data-testid=btn_resend")).to_be_enabled(timeout=3000)
        expect(page.locator("data-testid=btn_order_cancel")).to_be_enabled(timeout=3000)
    except Exception as e:
        error_message = f"❌ Error in test_order_status_fail: {str(e)}"
        print(error_message)
        raise  # 예외 재전파로 테스트 실패 처리
