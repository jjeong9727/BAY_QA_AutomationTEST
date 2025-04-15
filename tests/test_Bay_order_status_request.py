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
    # 제품 필터링 및 랜덤 선택
    eligible_products = filter_products_by_delivery_status(1)
    if not eligible_products:
        raise ValueError("No product found with delivery_status 1")
    
    target_product = random.choice(eligible_products)
    product_name = target_product['kor']

    try:
        # 로그인
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login", timeout=50000)
        page.wait_for_timeout(1000)

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        page.click("data-testid=drop_status_trigger")
        page.wait_for_selector("data-testid=drop_status_item", timeout=10000)  
        page.click('div[data-testid="drop_status_item"] div[data-value="발주 요청"]')
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"Order ID for product {product_name} not found")

        # 상태 확인
        expected_status_conditions = order_status_map["발주 요청"]
        check_order_status_by_order_id(page, "발주 요청", order_id, expected_status_conditions)

        print("UI 확인")

        # 수락 URL 접속
        order_url = f"{URLS['base_accept_url']}/{order_id}/accept"
        page.goto(order_url)

        # 정보 입력 및 수락
        page.fill("input[data-testid='input_name']", "권정의")
        page.fill("input[data-testid='input_contact']", "01062754153")
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(1000)
        page.click("button[data-testid='btn_accept']")
        page.wait_for_timeout(500)

        # 상태 재확인
        page.goto(URLS["bay_orderList"])
        page.wait_for_url(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # 상태 확인 로직
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "발주 진행", f"[FAIL] {product_name} 상태가 '발주 진행'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 발주 진행 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 상태 업데이트
        update_product_status_in_json(product_name, 2)

    except Exception as e:
        print(f"❌ Error in test_order_acceptance: {str(e)}")
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