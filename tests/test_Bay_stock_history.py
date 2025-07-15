import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

def get_have_stock_product(stock_manager, page):
    # 전체 상품 목록 가져오기
    all_products = stock_manager.load_product_from_json()

    # 조건에 맞는 상품 필터링
    filtered_products = [
        p for p in all_products
        if p.get("stock_qty", 0) >= 1 and p.get("order_flag", 1) != 0
    ]

    if not filtered_products:
        raise ValueError("조건에 맞는 상품이 없습니다.")

    # 랜덤으로 하나 선택
    product = random.choice(filtered_products)
    return product


def test_inflow_anotherday(page):
    bay_login(page)
    stock_manager = StockManager(page)

    product = get_have_stock_product(stock_manager, page)
    product_name = product["kor"]
    current_stock = product["stock_qty"]
    page.goto(URLS["bay_stock"])

    page.click("data-testid=btn_stockadd")
    page.wait_for_timeout(2000)
    # 과거 날짜 선택 
    yesterday = datetime.today() - timedelta(days=1)
    mmdd = yesterday.strftime("%m%d")  # MMDD 형식으로 변환
    txt_register = "해당 날짜로 재고 등록하시겠습니까?"
    page.locator("data-testid=select_date").click()
    page.wait_for_timeout(1000)
    yesterday = datetime.today() - timedelta(days=1)
    mmdd = yesterday.strftime("%m%d")  # MMDD 형식으로 변환
    today_str = yesterday.strftime("%Y. %m. %d") # YYYYMMDD 형식으로 변환
    page.locator(f"[data-testid=btn_day_{mmdd}]").click()
    page.wait_for_timeout(1000) 

    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name="입고", exact=True).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_prdname_search", product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item", has_text=product_name).click()
    expect(page.locator("data-testid=txt_current_stock")).to_have_text(str(current_stock), timeout=3000)
    instock = 100
    page.fill("data-testid=input_qty", str(instock))
    page.wait_for_timeout(500)
    expected = current_stock + instock
    page.fill("data-testid=input_memo", "과거 날짜 입고 확인 테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_register")).to_have_text(txt_register, timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 입고 후 재고 값을 json 파일에 저장
    update_product_flag(product['kor'], stock_qty=expected)

    page.fill("data-testid=input_search", product_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    first_row_cell = page.locator("table tbody tr").first.locator("td").nth(3)
    cell_text = first_row_cell.inner_text().strip().split("\n")[0]
    assert cell_text == product_name, f"❌ 검색 결과가 일치하지 않음: {cell_text} != {product_name}"
    first_row_cell = page.locator("table tbody tr").first.locator("td").nth(3)
    first_row_cell.locator("div").first.click()
    page.wait_for_timeout(3000)
    date_locator = page.locator("data-testid=txt_date").first
    print("📅 화면에 출력된 날짜:", date_locator.inner_text())
    expect(date_locator).to_have_text(today_str)    
    page.wait_for_timeout(1000)