from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, get_product_stock, get_latest_product_name

def verify_auto_order_triggered(page, product_name: str):
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
            update_product_flag(product_name, order_flag=True)  # ✅ 여기서 플래그 업데이트
            return

    raise AssertionError(f"[FAIL] 자동 발주 리스트에 '{product_name}' 제품 없음")


def test_stock_outflow(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    latest_product = get_latest_product_name()
    product_name = latest_product["kor"]
    safety_stock = latest_product.get("safety", 0)

    page.goto(URLS["bay_stock"])
    page.wait_for_url(URLS["bay_stock"], timeout=60000)
    current_stock = get_product_stock(page, product_name)

    # ✅ 출고 수량 계산: 출고 후 재고가 safety보다 작고 1 이상이어야 함
    outflow_qty = current_stock - safety_stock + 1
    if outflow_qty < 1:
        raise ValueError(f"[SKIP] 출고 수량 계산 불가 - 현재 재고: {current_stock}, 안전재고: {safety_stock}")

    page.click("data-testid=btn_stockAdd")
    page.wait_for_url(URLS["bay_stockAdd"], timeout=60000)

    page.locator("data-testid=drop_status").click()
    page.get_by_role("option", name="출고", exact=True).click()

    page.locator("data-testid=drop_prdname").click()
    page.get_by_role("option", name=product_name, exact=True).click()

    page.fill("data-testid=input_quantity", str(outflow_qty))
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_stock"], timeout=60000)

    # ✅ 재고 확인
    updated_stock = get_product_stock(page, product_name)
    expected = current_stock - outflow_qty
    assert updated_stock == expected, f"[FAIL] 출고 후 재고 불일치. 예상: {expected}, 실제: {updated_stock}"

    print(f"[PASS] 출고 처리 완료: {product_name}, 출고량: {outflow_qty}, 현재 재고: {updated_stock}")

    # ✅ 자동 발주 확인 및 플래그 설정
    if updated_stock < safety_stock:
        verify_auto_order_triggered(page, product_name)



def test_stock_outflow(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()
    stock_manager.search_product_by_name()a
    outflow_qty = stock_manager.initial_stock if stock_manager.initial_stock > 0 else 1
    stock_manager.perform_outflow(outflow_qty)

    updated = stock_manager.get_current_stock()
    expected = stock_manager.initial_stock - outflow_qty
    assert updated == expected, f"[FAIL] 출고 후 재고 오류: {expected} != {updated}"
    print(f"[PASS] 출고 확인: {stock_manager.display_product_name} → {updated}")

