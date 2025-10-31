import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

# def get_filtered_products(stock_manager, page):

products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3", "발주 거절 제품 1", "발주 거절 제품 2"]
def test_stock_inflow(page):
    try:
        bay_login(page, "jekwon")
        stock_manager = StockManager(page)
        if len(products) < 3:
            raise AssertionError(f"❌ 조건에 맞는 제품이 {len(products)}개만 존재합니다. 3개 이상이 필요합니다.")

        for product in products:
            print(product)
            stock_manager.product_name = product  # 제품명을 클래스 속성에 저장
            stock_manager.search_product_by_name(product)

            inflow_qty = random.randint(6, 10)  # 랜덤 입고 수량
            stock_manager.perform_inflow(inflow_qty)  

            updated = stock_manager.get_current_stock()
            expected = stock_manager.initial_stock + inflow_qty
            assert updated == expected, f"[FAIL] {product} 입고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 입고 확인: {product} → {updated}")

            # # 입고 후 재고 값을 json 파일에 저장
            # update_product_flag(product, stock_qty=expected)

    except Exception as e:
        print(f"❌ 입고 테스트 실패: {str(e)}")
        raise

def test_inflow_bulk (page:Page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stock"])
    page.wait_for_selector("[data-testid=\'btn_stockadd\']", timeout=7000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_selector("[data-testid=\'drop_status_trigger\']", timeout=5000)
    product_list = [f"배치 확인 제품 {i:02d}" for i in range(1, 10)]  # 01~09번 제품 리스트 생성
    product_list.extend(["발주 거절 제품 3", "발주 삭제 제품 1"])
    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="입고", exact=True).click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)
        
        # 입고량 계산 
        inflow_qty = 10

        page.locator("data-testid=input_qty").last.fill(str(inflow_qty))
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 입고")
        page.wait_for_timeout(1000)

        if idx < len(product_list) - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)
    txt_inflow = f"{len(product_list)}개의 재고 입고가 완료되었습니다."
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_inflow")).to_have_text(txt_inflow, timeout=10000)
    page.wait_for_timeout(2000)
