import random
from config import URLS, Account
from helpers.stock_utils import StockManager


def test_stock_inflow(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    stock_manager = StockManager(page)
    stock_manager.load_product_from_json()
    stock_manager.search_product_by_name()

    inflow_qty = random.randint(1, 10)
    stock_manager.perform_inflow(inflow_qty)

    updated = stock_manager.get_current_stock()
    expected = stock_manager.initial_stock + inflow_qty
    assert updated == expected, f"[FAIL] 입고 후 재고 오류: {expected} != {updated}"
    print(f"[PASS] 입고 확인: {stock_manager.display_product_name} → {updated}")
