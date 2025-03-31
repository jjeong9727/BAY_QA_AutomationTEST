from config import URLS, Account
from helpers.stock_utils import get_current_stock
import random

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

def perform_stock_outflow(page: Page, product_data: dict):
    product_name = product_data["kor"]
    safety = product_data.get("safety", 0)

    # 현재 재고 조회
    current_stock = get_current_stock(page, product_name)

    # 출고 후 재고가 safety 미만 & 1 이상 되도록 출고 수량 계산
    max_outflow = current_stock - 1
    min_outflow = current_stock - safety + 1
    if min_outflow < 1:
        min_outflow = 1

    if min_outflow > max_outflow:
        raise ValueError(f"❌ 출고 조건을 만족하는 수량이 없습니다. 현재 재고: {current_stock}, safety: {safety}")

    stock_out_qty = random.randint(min_outflow, max_outflow)
    print(f"[출고] 제품: {product_name}, 현재 재고: {current_stock}, 출고 수량: {stock_out_qty}, 출고 후 재고: {current_stock - stock_out_qty}, safety: {safety}")

    # 출고 등록 페이지 진입
    page.goto(URLS["bay_stock"])
    page.click("data-testid=btn_stockAdd")
    page.wait_for_url(URLS["bay_stockAdd"], timeout=10000)

    # 출고 상태 선택
    page.locator("data-testid=drop_status").click()
    page.get_by_role("option", name="출고", exact=True).click()

    # 제품 선택
    page.locator("data-testid=drop_prdname").click()
    page.get_by_role("option", name=product_name, exact=True).click()

    # 수량 입력 및 저장
    page.fill("data-testid=input_quantity", str(stock_out_qty))
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_stock"], timeout=10000)

    # 출고 후 재고 확인
    updated_stock = get_current_stock(page, product_name)
    expected_stock = current_stock - stock_out_qty
    assert updated_stock == expected_stock, f"[FAIL] 출고 후 재고 불일치: 예상={expected_stock}, 실제={updated_stock}"
    print(f"[PASS] 출고 완료 → {product_name} / 현재 재고: {updated_stock}")

    if updated_stock < safety:
        verify_auto_order_triggered(page, product_name)