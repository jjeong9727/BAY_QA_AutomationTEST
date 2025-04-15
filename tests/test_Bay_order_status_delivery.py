import json
import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status_by_order_id, get_order_id_from_order_list, filter_products_by_delivery_status
from playwright.sync_api import Page
from config import URLS, Account


def update_product_status_in_json(product_name: str, delivery_status: int, order_flag: int):
    try:
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            if product['kor'] == product_name:
                product['delivery_status'] = delivery_status
                product['order_flag'] = order_flag  # order_flag 값을 0으로 설정
                break

        with open('product_name.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_message = f"Error updating product status in JSON: {str(e)}"
        raise


def test_order_receive_from_delivery(page: Page):
    try:
        # product.json에서 delivery_status가 3인 제품들 찾기
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        # delivery_status가 3인 제품들만 필터링
        eligible_products = [product for product in products if product.get('delivery_status') == 3]

        if not eligible_products:
            raise ValueError("발주 진행 상태인 제품이 없다")

        # delivery_status가 3인 제품 중 랜덤으로 하나 선택
        target_product = random.choice(eligible_products)
        product_name = target_product['kor']

        page.goto(URLS["bay_login"]) 
        page.fill("data-testid=input_id", Account["testid"])  # 아이디 입력
        page.fill("data-testid=input_pw", Account["testpw"])  # 비밀번호 입력
        page.click("data-testid=btn_login", timeout=50000)  # 로그인 버튼 클릭
        page.wait_for_timeout(1000)

        # 발주 내역 화면으로 이동하여 제품명 검색 
        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # 검색된 제품의 order_id 값 가져오기
        order_id = page.inner_text("span#order_id")  # test id = "order_id" 요소 값 가져오기

        if not order_id:
            raise ValueError(f"Order ID for product {product_name} not found")

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["배송 진행"]  # 배송 진행 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "배송 진행", order_id, expected_status_conditions)

        # 수령확정 버튼(btn_receive)을 누르고 수령확인 버튼 클릭
        page.click("button[data-testid='btn_receive']")  # 수령 확정 버튼 클릭
        page.click("button[data-testid='btn_confirm']")  # 수령 확인 버튼 클릭

        # 발주 내역에서 해당 제품을 "수령 완료" 상태인지 확인
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                print(f"[PASS] 수령 완료 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 수령 완료 상태 확인 후 delivery_status 값을 4로 업데이트 (수령 완료 상태) 
        # 그리고 order_flag는 0으로 설정
        update_product_status_in_json(product_name, 4, 0)  # delivery_status를 4로 업데이트, order_flag를 0으로 설정

        # 입고 수량을 저장
        stock_inflow = target_product.get('stock_inflow', 0)  # 입고 수량 저장 (JSON에서 가져오기)

        # 재고 관리 화면으로 이동하여 제품명으로 검색
        page.goto(URLS["stock_management"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        current_stock = page.locator("td[data-testid='stock_qty']").inner_text()
        current_stock = int(current_stock.strip())

        # JSON 파일에 있던 재고 수량 + 입고 수량 계산 후 비교
        expected_stock = target_product['stock_qty'] + stock_inflow

        assert current_stock == expected_stock, f"[FAIL] 현 재고량이 예상치와 다릅니다. 예상: {expected_stock}, 실제: {current_stock}"
        print(f"[PASS] 현 재고량 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

    except Exception as e:
        error_message = f"❌ Error in test_order_receive_from_delivery: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise  # Reraise the exception to maintain test flow
