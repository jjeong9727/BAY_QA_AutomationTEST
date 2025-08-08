import json
import random
from datetime import datetime
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status, get_order_id_from_order_list, 
    check_order_status_by_order_id, search_order_history
)
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
        raise RuntimeError(f"Error updating product status in JSON: {str(e)}")


def test_order_receive_from_progress(page: Page):
    try:
        # delivery_status가 2인 제품 필터링
        eligible_products = filter_products_by_delivery_status(2)
        if not eligible_products:
            raise ValueError("발주 진행 상태인 제품이 없습니다.")
        status_name = "발주 진행"

        # 대상 제품 선택
        target_product = random.choice(eligible_products)
        product_name = target_product['kor']
        previous_stock = target_product.get('stock_qty', 0)

        bay_login(page)

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(1000)
        search_order_history(page, product_name, status_name)

        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID를 찾을 수 없습니다.")

        # 상태 확인: 배송 진행
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        
        # 수령확정 버튼(btn_receive)을 누르고 수령확인 버튼 클릭
        page.click("button[data-testid='btn_receive']")  # 수령 확정 버튼 클릭
        expect(page.locator("data-testid=input_quantity")).to_be_visible(timeout=5000)
        stock_inflow = int(page.locator('[data-testid="input_quantity"]').input_value())#입고 수량 저장
        print(stock_inflow)
        # 발주 수령 팝업 퀵메뉴 버튼 확인
        page.locator("data-testid=btn_plus_10").click()
        new_data = stock_inflow + 10
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_plus_100").click() 
        new_data += 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_100").click() 
        new_data -= 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_10").click() 
        new_data -= 10 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        assert new_data == stock_inflow, f"초기 수량과 동일하지 않음. 초기 수량: {stock_inflow}, 현재 수량: {new_data}"
        page.click("button[data-testid='btn_confirm']")  # 수령 확인 버튼 클릭
        page.wait_for_timeout(2000)
        

        # 수령 상태 확인
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
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "수령 완료", f"[FAIL] {product_name} 상태가 '수령 완료'가 아님 → 현재 상태: {status}"
                print(f"[PASS] 수령 완료 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # JSON 상태 업데이트
        update_product_status_in_json(product_name, delivery_status=7, order_flag=0)

        # 재고 관리 → 재고 확인
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        current_stock_text = page.locator("table tbody tr td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        expected_stock = previous_stock + stock_inflow
        assert current_stock == expected_stock, f"[FAIL] 재고 불일치: 예상 {expected_stock}, 실제 {current_stock}"
        print(f"[PASS] 재고 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

        # JSON 재고량 업데이트
        with open('product_name.json', 'r', encoding='utf-8') as f:
            products = json.load(f)

        for product in products:
            if product['kor'] == product_name:
                product['stock_qty'] = current_stock
                break

        with open('product_name.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print("[PASS] JSON 파일 재고량 업데이트 완료")

    except Exception as e:
        print(f"❌ Error in test_order_receive_and_inventory_check: {str(e)}")
        raise


def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False)

        test_order_receive_from_progress(page)
        page.close()


if __name__ == "__main__":
    main()
