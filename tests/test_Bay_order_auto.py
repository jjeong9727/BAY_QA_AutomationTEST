from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, get_product_stock, get_latest_product_name
from helpers.save_test_result import save_test_result  

def verify_auto_order_triggered(page, product_name: str):
    try:
        page.goto(URLS["bay_orderList"])
        page.wait_for_url(URLS["bay_orderList"], timeout=60000)

        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                
                assert status == "발주 요청", f"[FAIL] {product_name} 상태가 '발주 요청'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 자동 발주 확인 완료 → {product_name} 상태: {status}")
                
                # 제품 상태 업데이트
                update_product_flag(product_name, order_flag=1, order_status=1)
                return

        raise AssertionError(f"[FAIL] 자동 발주 리스트에 '{product_name}' 제품 없음")

    except AssertionError as e:
        error_message = f"AssertionError: {str(e)}"
        print(error_message)
        # 실패한 테스트 결과를 저장
        save_test_result("verify_auto_order_triggered", error_message, status="FAIL")
        raise 

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        # 실패한 테스트 결과를 저장
        save_test_result("verify_auto_order_triggered", error_message, status="ERROR")
        raise 
