import json
import random
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import filter_products_by_delivery_status, get_order_id_from_order_list, check_order_status_by_order_id
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login


def update_product_status_in_json(product_name: str, delivery_status: int, order_flag: int):
    try:
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            if product['kor'] == product_name:
                product['delivery_status'] = delivery_status
                product['order_flag'] = order_flag
                break

        with open('product_name.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_message = f"Error updating product status in JSON: {str(e)}"
        raise


def test_order_cancel(page: Page):
    try:
        # JSON 파일에서 제품명 불러오기
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        # delivery_status가 1인 제품들 필터링
        eligible_products = [product for product in products if product.get('delivery_status') == 1]

        if not eligible_products:
            raise ValueError("No product found with delivery_status 1")

        # delivery_status가 1인 제품 중 랜덤으로 하나 선택
        target_product = random.choice(eligible_products)
        product_name = target_product['kor']

        # 발주 내역 화면으로 이동하여 제품명 검색 후 order_id 가져오기
        bay_login(page)
        
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(3000)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=8000)

        # 검색된 제품의 order_id 값 가져오기
        order_id = get_order_id_from_order_list(page, product_name)
        
        if not order_id:
            raise ValueError(f"Order ID for product {product_name} not found")

        # 취소 버튼
        page.click("button[data-testid='btn_cancel']")  # 취소 버튼 클릭
        btn = page.locator("button[data-testid='btn_confirm']")
        expect(btn).to_be_visible(timeout=3000)
        btn.scroll_into_view_if_needed()
        btn.click()

        page.wait_for_timeout(5000)

        # 발주 내역에서 해당 제품을 "발주 취소" 상태인지 확인
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

        # 발주 진행 상태 확인 후 delivery_status 값을 5로 업데이트 (발주 취소 상태)
        update_product_status_in_json(product_name, delivery_status=5, order_flag=0)  # delivery_status를 5로 업데이트 (발주 취소), order_flag=0

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
