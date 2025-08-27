import json
import re
from datetime import datetime, timedelta
import time
import random
from pathlib import Path
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status, get_order_id_from_order_list, check_order_status_by_order_id,
    search_order_history
)
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login
from datetime import datetime
BATCH_PATH = Path("batch_time.json")
def load_batch_time(path: Path = BATCH_PATH) -> tuple[str, str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj["hour"], obj["minute"]  # "HH", "MM"
hour_str, minute_str = load_batch_time()
def is_target_passed_now(hour_str: str, minute_str: str) -> bool:
    now = datetime.now()
    target_today = now.replace(
        hour=int(hour_str), minute=int(minute_str), second=0, microsecond=0
    )
    return now >= target_today

if not is_target_passed_now(hour_str, minute_str):
    # 아직 안 지났으면 목표 시각 + 1분까지 대기
    
    now = datetime.now()
    target = now.replace(hour=int(hour_str), minute=int(minute_str), second=0, microsecond=0)
    time.sleep(max(0, (target - now).total_seconds()) + 60)  # +60s 여유



def test_order_acceptance(page: Page):
    

    status_name = "발주 요청"
    selected_products = ["자동화개별제품_2", "자동화개별제품_3"]
    names = ["권정의B", "권정의C"]
    phone = "01062754153"

    for product in selected_products:
        product_name = product
        if product == "자동화개별제품_2":
            name = names[0]
        else:
            name = names[1]

        try:
            # 로그인
            bay_login(page)

            # 발주 내역 검색
            page.goto(URLS["bay_orderList"])
            page.wait_for_timeout(2000)

            search_order_history(page, product_name, status_name)

            # order_id 추출
            order_id = get_order_id_from_order_list(page, product_name)
            if not order_id:
                raise ValueError(f"Order ID for '{product_name}'를 찾을 수 없습니다.")

            # 상태 확인
            expected_status_conditions = order_status_map["발주 요청"]
            check_order_status_by_order_id(page, "발주 요청", order_id, expected_status_conditions)

            # 재발송 확인
            txt_resend = "재발송하시겠습니까?"
            page.locator("data-testid=btn_resend").click()
            expect(page.locator("data-testid=txt_resend")).to_have_text(txt_resend, timeout=3000)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=toast_resend")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

            # 수락 URL 접속 및 처리
            accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
            page.goto(accept_url)
            expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
            page.fill("input[data-testid='input_name']", name)
            page.wait_for_timeout(1000)
            page.fill("input[data-testid='input_contact']", phone)
            page.wait_for_timeout(1000)
            page.locator("button[data-testid='btn_confirm']").last.click()
            expect(page.locator("button[data-testid='btn_accept']")).to_be_visible(timeout=7000)
            page.wait_for_timeout(1000)
            page.click("button[data-testid='btn_accept']")
            expect(page.locator("data-testid=toast_accept")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

            # 발주 상태 재확인
            page.goto(URLS["bay_orderList"])
            expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
            page.wait_for_timeout(1000)
            page.fill("data-testid=input_search", product_name)
            page.wait_for_timeout(500)
            page.click("data-testid=btn_search")
            expect(page.locator("data-testid=history").first).to_be_visible(timeout=8000)
            page.wait_for_timeout(1000)

            rows = page.locator("table tbody tr")
            found = False
            for i in range(rows.count()):
                row = rows.nth(i)
                columns = row.locator("td").all_inner_texts()
                if product_name in columns[1]:
                    status = columns[0].strip()
                    assert status == "발주 진행", f"{product_name} 상태가 '발주 진행'이 아님 → 현재 상태: {status}"
                    print(f"[PASS] {product_name} → 발주 진행 상태 확인 완료")
                    found = True
                    break

            if not found:
                raise AssertionError(f"제품 '{product_name}'을 발주 내역에서 찾을 수 없습니다.")

            # # JSON 업데이트
            # update_product_status_in_json(product_name, 2)

            
        except Exception as e:
            print(f"❌ {product_name} 처리 중 오류 발생: {str(e)}")
            raise



def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False)
        # 배송 진행 상태로 업데이트 작업을 하나의 함수에서 처리
        test_order_acceptance(page)

        page.close()


if __name__ == "__main__":
    main()