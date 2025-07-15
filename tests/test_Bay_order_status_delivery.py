import json
import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    check_order_status_by_order_id, get_order_id_from_order_list, search_order_history
)
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login


def update_product_status_in_json(product_name: str, delivery_status: int, order_flag: int, stock_quantity=int):
    try:
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            if product['kor'] == product_name:
                product['delivery_status'] = delivery_status
                product['order_flag'] = order_flag  # order_flag 값을 0으로 설정
                product['stock_qty'] = stock_quantity
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
        status_name = "배송 진행"

        # delivery_status가 3인 제품들만 필터링
        eligible_products = [product for product in products if product.get('delivery_status') == 3]

        if not eligible_products:
            raise ValueError("배송 진행 상태인 제품이 없다")

        # delivery_status가 3 제품 중 랜덤으로 하나 선택
        target_product = random.choice(eligible_products)
        product_name = target_product['kor']

        bay_login(page)

        # 발주 내역 화면으로 이동하여 제품명 검색 
        page.goto(URLS["bay_orderList"])
        search_order_history(page, product_name, status_name)
        
        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["배송 진행"]  # 배송 진행 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "배송 진행", order_id, expected_status_conditions)

        # 수령확정 버튼(btn_receive)을 누르고 수령확인 버튼 클릭
        page.click("button[data-testid='btn_receive']")  # 수령 확정 버튼 클릭
        expect(page.locator("data-testid=input_quantity")).to_be_visible(timeout=5000)
        stock_inflow = int(page.locator('[data-testid="input_quantity"]').input_value())#입고 수량 저장
        print(stock_inflow)

        page.click("button[data-testid='btn_confirm']")  # 수령 확인 버튼 클릭
        page.wait_for_timeout(2000)

        # 발주 내역에서 해당 제품을 "수령 확정" 상태인지 확인
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000) 
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000) 
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                print(f"[PASS] 수령 확정 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 재고 관리 화면으로 이동하여 제품명으로 검색
        page.goto(URLS["bay_stock"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        current_stock_text = page.locator("table tbody tr td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        # JSON 파일에 있던 재고 수량 + 입고 수량 계산 후 비교
        expected_stock = target_product['stock_qty'] + stock_inflow

        # 수령 완료 상태 확인 후 delivery_status 값을 4로 업데이트 (수령 완료 상태) 
        # 그리고 order_flag는 0으로 설정
        update_product_status_in_json(product_name, delivery_status=4, order_flag=0, stock_quantity=expected_stock)  # delivery_status를 4로 업데이트, order_flag를 0으로 설정


        assert current_stock == expected_stock, f"[FAIL] 현 재고량이 예상치와 다릅니다. 예상: {expected_stock}, 실제: {current_stock}"
        print(f"[PASS] 현 재고량 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

    except Exception as e:
        error_message = f"❌ Error in test_order_receive_from_delivery: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise  # Reraise the exception to maintain test flow
