import json
import random
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import (
    check_order_status_by_order_id, get_order_id_from_order_list, search_order_history
)
from helpers.approve_utils import check_approval_status_buttons
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.common_utils import bay_login
suppliers = ["자동화업체A, 권정의A 010-6275-4153", "자동화업체B, 권정의B 010-6275-4153", "자동화업체C, 권정의C 010-6275-4153"]


# 배송 진행 상태에서 수령
def test_order_receive_from_delivery(page: Page):
    try:
        product_name = "자동화개별제품_2"
        status_name = "배송 진행"

        bay_login(page, "jekwon")
        page.goto(URLS["bay_stock"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        first_row = page.locator("table tbody tr").first
        previous_stock_text = first_row.locator("td:nth-child(6)").inner_text()

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
                print(f"[PASS] 수령 완료 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 재고 관리 화면으로 이동하여 제품명으로 검색
        page.goto(URLS["bay_stock"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        first_row = page.locator("table tbody tr").first
        current_stock_text = first_row.locator("td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        # JSON 파일에 있던 재고 수량 + 입고 수량 계산 후 비교
        expected_stock =  int(previous_stock_text)+ int(stock_inflow)

        assert current_stock == expected_stock, f"[FAIL] 현 재고량이 예상치와 다릅니다. 예상: {expected_stock}, 실제: {current_stock}"
        print(f"[PASS] 현 재고량 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

        # 수령완료 후 발주 예정 내역의 "수령완료"상태 확인
        check_approval_status_buttons(page, "수령 완료", product_name, "자동화규칙_개별", False, False)


    except Exception as e:
        error_message = f"❌ Error in test_order_receive_from_delivery: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise  # Reraise the exception to maintain test flow

# 발주 진행 상태에서 수령 
def test_order_receive_from_progress(page: Page):
    try:
        product_name = "자동화개별제품_3"
        status_name = "발주 진행"

        bay_login(page, "jekwon")
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        previous_stock = page.locator("table tbody tr td:nth-child(6)").inner_text()

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


        # 재고 관리 → 재고 확인
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        current_stock_text = page.locator("table tbody tr td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        expected_stock = int(previous_stock) + stock_inflow
        assert current_stock == expected_stock, f"[FAIL] 재고 불일치: 예상 {expected_stock}, 실제 {current_stock}"
        print(f"[PASS] 재고 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

        # 수령완료 후 발주 예정 내역의 "수령완료"상태 확인
        check_approval_status_buttons(page, "수령 완료", product_name, "자동화규칙_개별", False, False)   


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
