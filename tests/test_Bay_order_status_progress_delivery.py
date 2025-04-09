import json
import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status_by_order_id, get_order_id_from_order_list, filter_products_by_delivery_status
from helpers.save_test_result import save_test_result  
from playwright.sync_api import Page, sync_playwright

def update_product_status_in_json(product_name: str, delivery_status: int):
    try:
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        for product in products:
            if product['product_name'] == product_name:
                product['delivery_status'] = delivery_status
                break
        
        with open('product_name.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
    
    except Exception as e:
        error_message = f"Error updating product status in JSON: {str(e)}"
        save_test_result("update_product_status_in_json", error_message, status="ERROR")
        raise

def test_order_delivery_and_update_status(page: Page):
    try:
        # product.json에서 delivery_status가 2인 제품들 찾기
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # delivery_status가 2인 제품들만 필터링
        eligible_products = [product for product in products if product.get('delivery_status') == 2]
        
        if not eligible_products:
            raise ValueError("No product found with delivery_status 2")

        # delivery_status가 2인 제품 중 랜덤으로 하나 선택
        target_product = random.choice(eligible_products)
        product_name = target_product['product_name']

        # 발주 내역 화면으로 이동하여 제품명 검색 후 order_id 가져오기
        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)
        
        # 검색된 제품의 order_id 값 가져오기
        order_id = page.inner_text("span#order_id")  # test id = "order_id" 요소 값 가져오기
        
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["발주 진행"]  # 발주 진행 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)
        
        # 기존 URL에 order_id 값을 추가하여 진입
        order_url = f"{URLS['base_order_url']}/{order_id}"
        page.goto(order_url)

        # 사용자 정보 입력 후 본인 인증
        page.fill("input[data-testid='input_name']", "권정의")
        page.fill("input[data-testid='input_contact']", "01062754153")
        page.click("button[data-testid='btn_confirm']")

        # 운송장 등록
        page.click("button[data-testid='drop_shipping']")  
        page.click("li[data-testid='drop_shipping_item']:first-child")  
        page.fill("input[data-testid='input_tracking']", "1234567890") 
        page.click("button[data-testid='btn_confirm']")  

        # 발주 내역 페이지로 돌아가서 해당 제품을 검색하여 상태 확인
        page.goto(URLS["bay_orderList"])
        page.wait_for_url(URLS["bay_orderList"])

        # 발주 내역에서 해당 제품을 "배송 진행" 상태인지 확인
        page.fill("data-testid=input_search", product_name)  # 제품명으로 검색
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)  # 검색 후 잠시 대기

        # 검색 결과에서 해당 제품의 상태를 확인
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                assert status == "배송 진행", f"[FAIL] {product_name} 상태가 '배송 진행'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 배송 진행 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 배송 진행 상태 확인 후 delivery_status 값을 3으로 업데이트 (배송 진행 상태)
        update_product_status_in_json(product_name, 3)  # delivery_status를 3으로 업데이트 (배송 진행)

    except Exception as e:
        error_message = f"❌ Error in test_order_delivery_and_update_status: {str(e)}"
        print(error_message)
        
        # 실패한 테스트 결과를 저장
        save_test_result("test_order_delivery_and_update_status", error_message, status="FAIL")
        raise  # Reraise the exception to maintain test flow

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 배송 진행 상태로 업데이트 작업을 하나의 함수에서 처리
        test_order_delivery_and_update_status(page)
        
        browser.close()

if __name__ == "__main__":
    main()
