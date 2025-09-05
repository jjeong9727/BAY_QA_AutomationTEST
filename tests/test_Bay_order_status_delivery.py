import json
import re
import random
from playwright.sync_api import Page, sync_playwright, expect 
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id,
    search_order_history
)
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login

suppliers = ["자동화업체A, 권정의A 010-6275-4153", "자동화업체B, 권정의B 010-6275-4153", "자동화업체C, 권정의C 010-6275-4153"]
product_name = "자동화개별제품_2"
name = "권정의B"
phone = "01062754153"


def test_order_delivery(page: Page):
    try:

        # 로그인
        bay_login(page, "jekwon")

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        # search_order_history(page, product_name, "발주 진행")

        # # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 발주 상태 확인: '발주 진행'
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        # 배송 URL 진입
        tracking_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)

        # 본인 인증
        page.fill("input[data-testid='input_name']", name)
        page.fill("input[data-testid='input_contact']", phone)
        page.click("button[data-testid='btn_confirm']")
        expect(page.locator("data-testid=drop_shipping_trigger")).to_be_visible(timeout=5000)

        # 배송사 선택 드롭다운 열기
        carrier_name = "일양로지스"
        tracking = "1234567890"
        new_carrier = "직접 배송"
        new_tracking = "직접 배송은 운송장 번호가 불필요합니다"
        page.locator("data-testid=drop_shipping_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_search").fill(carrier_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_item", has_text=carrier_name).click()
        page.wait_for_timeout(1000)
        
        page.fill("input[data-testid='input_tracking']", tracking)
        page.wait_for_timeout(3000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        expect(page.locator("data-testid=toast_tracking")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        # 상태 확인: 배송 진행
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(500)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(500)

        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "배송 진행", f"[FAIL] {product_name} 상태가 '배송 진행'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 배송 진행 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break
        

        # 택배사 + 운송장 확인
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(2000)
        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(carrier_name, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text(tracking, timeout=3000)
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_copy").click()
        expect(page.locator("data-testid=toast_copy")).to_have_text("운송장 번호가 복사되었습니다.", timeout=3000)

        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        # 운송정보 수정 후 확인 (직접 발주로 변경)
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_name']", name)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", phone)
        page.wait_for_timeout(1000)
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(1000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_search").fill(new_carrier)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_item", has_text=new_carrier).click()
        page.wait_for_timeout(1000)
        expect(page.locator("input[data-testid='input_tracking']")).to_have_attribute("placeholder", new_tracking, timeout=3000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(2000)

        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(new_carrier, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text("-", timeout=3000)

        # 직접 배송인 경우 비활성화 
        expect(page.locator("data-testid=btn_copy")).to_be_disabled(timeout=3000)

        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

    except Exception as e:
        print(f"❌ Error in test_order_delivery: {str(e)}")
        raise

def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False)

        test_order_delivery(page)
        page.close()

if __name__ == "__main__":
    main()
