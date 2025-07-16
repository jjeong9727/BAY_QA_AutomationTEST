import json
import random
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status, get_order_id_from_order_list, check_order_status_by_order_id,
    search_order_history
)
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login
from datetime import datetime

# 발주 진행 상태 코드
    # 1: 발주 요청
    # 2: 발주 진행
    # 3: 배송 진행 
    # 4: 수령 완료(운송장O) 3 -> 4
    # 5: 배송 취소
    # 6: 배송 실패
    # 7: 수령 완료(운송장X) 2 -> 7

def update_product_status_in_json(product_name: str, delivery_status: int):
    try:
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            if product['kor'] == product_name:
                product['delivery_status'] = delivery_status
                break

        with open('product_name.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    except Exception as e:
        raise RuntimeError(f"Error updating product status in JSON: {str(e)}")


def test_order_acceptance(page: Page):
    # 발주 요청 상태(1)인 제품 2개 선택
    eligible_products = filter_products_by_delivery_status(1)
    if len(eligible_products) < 2:
        raise ValueError("delivery_status가 1인 제품이 2개 미만입니다.")
    status_name = "발주 요청"
    selected_products = random.sample(eligible_products, 2)

    for product in selected_products:
        product_name = product['kor']
        stock = product['stock_qty']

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
            page.fill("input[data-testid='input_name']", "권정의")
            page.wait_for_timeout(1000)
            page.fill("input[data-testid='input_contact']", "01062754153")
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

            # JSON 업데이트
            update_product_status_in_json(product_name, 2)

            # 안전 재고 수정 > 발주 불가 확인
            txt_order = "자동 발주를 진행하시겠습니까?"
            page.goto(URLS["bay_prdList"])
            page.wait_for_timeout(2000)
            page.fill('[data-testid="input_search"]', product_name)
            page.wait_for_timeout(500)
            page.click('[data-testid="btn_search"]')
            page.wait_for_timeout(1000)

            rows = page.locator("table tbody tr")
            row_count = rows.count()

            for i in range(row_count):
                edit_button = rows.nth(i).locator("td:nth-child(11) >> text=수정")
                if edit_button.is_visible():
                    print(f"✅ {i}번째 행의 수정 버튼 클릭")
                    edit_button.click()
                    break
            
            page.locator("data-testid=input_stk_safe").fill(str(300))
            page.wait_for_timeout(1000)
            page.locator("data-testid=btn_save").click()
            expect(page.locator("data-testid=txt_order")).to_have_text(txt_order, timeout=3000)
            page.wait_for_timeout(1000)

            page.locator("data-testid=btn_confirm").click()
            page.wait_for_timeout(1000)
            expect(page.locator("data-testid=toast_edit_noorder")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

            # 발주 진행 제품 삭제 불가 확인
            if stock ==0:
                page.fill('[data-testid="input_search"]', product_name)
                page.wait_for_timeout(1000)
                page.click('[data-testid="btn_search"]')
                page.wait_for_timeout(1000)

                rows = page.locator("table tbody tr")
                row_count = rows.count()

                for i in range(row_count):
                    delete_button = rows.nth(i).locator("td:nth-child(11) >> text=삭제")
                    if delete_button.is_visible():
                        print(f"✅ {i}번째 행의 삭제 버튼 클릭")
                        delete_button.click()
                        page.wait_for_timeout(1000)
                        break
                page.locator("data-testid=btn_del").click()                
                expect(page.locator("data-testid=toast_order")).to_be_visible(timeout=3000)
                page.wait_for_timeout(1000)
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