import json
import random
from playwright.sync_api import Page, sync_playwright
from config import URLS, Account
from helpers.order_status_utils import filter_products_by_delivery_status, get_order_id_from_order_list, check_order_status_by_order_id
from helpers.order_status_data import order_status_map


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

    selected_products = random.sample(eligible_products, 2)

    for product in selected_products:
        product_name = product['kor']

        try:
            # 로그인
            page.goto(URLS["bay_login"])
            page.fill("data-testid=input_id", Account["testid"])
            page.fill("data-testid=input_pw", Account["testpw"])
            page.click("data-testid=btn_login")
            page.wait_for_timeout(1000)

            # 발주 내역 검색
            page.goto(URLS["bay_orderList"])
            page.wait_for_timeout(500)
            page.click("data-testid=drop_status_trigger")
            page.wait_for_timeout(500)
            page.click('div[data-testid="drop_status_item"] div[data-value="발주 요청"]')
            page.wait_for_timeout(500)
            page.fill("data-testid=input_search", product_name)
            page.click("data-testid=btn_search")
            page.wait_for_timeout(1000)

            # order_id 추출
            order_id = get_order_id_from_order_list(page, product_name)
            if not order_id:
                raise ValueError(f"Order ID for '{product_name}'를 찾을 수 없습니다.")

            # 상태 확인
            expected_status_conditions = order_status_map["발주 요청"]
            check_order_status_by_order_id(page, "발주 요청", order_id, expected_status_conditions)

            # 수락 URL 접속 및 처리
            accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
            page.goto(accept_url)
            page.fill("input[data-testid='input_name']", "권정의")
            page.fill("input[data-testid='input_contact']", "01062754153")
            page.locator("button[data-testid='btn_confirm']").last.click()
            page.wait_for_timeout(500)
            page.click("button[data-testid='btn_accept']")
            page.wait_for_timeout(500)

            # 발주 상태 재확인
            page.goto(URLS["bay_orderList"])
            page.fill("data-testid=input_search", product_name)
            page.click("data-testid=btn_search")
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

        except Exception as e:
            print(f"❌ {product_name} 처리 중 오류 발생: {str(e)}")
            raise



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 배송 진행 상태로 업데이트 작업을 하나의 함수에서 처리
        test_order_acceptance(page)

        browser.close()


if __name__ == "__main__":
    main()