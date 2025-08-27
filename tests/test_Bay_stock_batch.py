import time
from config import URLS, Account
from pathlib import Path
from datetime import datetime, timedelta
from helpers.order_status_utils import search_order_history
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
from helpers.approve_utils import check_approval_history, check_order_pending_history


def test_inflow (page:Page):
    bay_login(page)
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_timeout(2000)
    # product_list = [f"자동화제품_{i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성
    product_list = [f"배치 확인 제품 {i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성
    product_list.extend(["발주 거절 제품 3", "발주 삭제 제품 1", "발주 삭제 제품 2"])
    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="입고", exact=True).click()
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(500)
        
        # 입고량 계산 
        inflow_qty = 10

        page.locator("data-testid=input_qty").last.fill(str(inflow_qty))
        page.wait_for_timeout(500)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 입고")
        page.wait_for_timeout(500)

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

def test_outflow(page:Page):
    bay_login(page)
    # 출고 처리 (발주 규칙은 test_Bay_stock_out.py 에서)
    txt_outflow = "재고가 안전 재고보다 적은 경우 발주 규칙에 따라 발주됩니다."
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_timeout(2000)
    # product_list = [f"자동화제품_{i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성
    product_list = [f"배치 확인 제품 {i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성

    product_list.extend(["발주 거절 제품 3", "발주 삭제 제품 1", "발주 삭제 제품 2"])

    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").last.click()
        page.wait_for_timeout(500)
        page.get_by_role("option", name="출고", exact=True).click()
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(500)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(500)
        # 현재 재고 텍스트 가져오기
        stock_text = page.locator('[data-testid="txt_current_stock"]').last.text_content()
        # 쉼표 제거하고 숫자로 변환
        current_stock = int(stock_text.replace(",", "").strip())
        # 출고량 = 현 재고수량 
        outflow_qty = current_stock

        page.locator("data-testid=input_qty").last.fill(str(outflow_qty))
        page.wait_for_timeout(500)
        page.locator("data-testid=input_memo").last.fill(f"{product} 제품 출고")
        page.wait_for_timeout(500)

        if idx < len(product_list) - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)
                page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_outflow")).to_have_text(txt_outflow, timeout=10000)
    page.wait_for_timeout(1000)
    # 발주 내역 미노출 확인 
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)

    today_btn_id = datetime.now().strftime("btn_day_%m%d")  # 예: btn_day_0710
    
    page.locator("[data-testid=select_startday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)
    
    page.locator("[data-testid=select_endday]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid={today_btn_id}]").click()
    page.wait_for_timeout(500)

    expect(page.locator("data-testid=drop_status_trigger")).to_be_visible(timeout=8000)
    page.locator("data-testid=drop_status_trigger").click()
    expect(page.locator("data-testid=drop_status_item")).to_be_visible(timeout=5000)
    page.locator('[role="option"]').filter(has_text="발주 요청").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill("자동화제품_3")
    page.wait_for_timeout(500)

    page.locator("[data-testid=btn_search]").click()
    page.wait_for_timeout(2000)

    expect(page.locator("data-testid=history")).not_to_be_visible(timeout=5000)

    # 발주 예정 내역 노출 확인 
    page.goto(URLS["bay_order_pending"])
    page.wait_for_selector("data-testid=input_search", timeout=5000)

    for idx, product in enumerate(product_list, start=1):
        if idx in (3, 6, 9): 
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, True)
        elif idx == 10:
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, False)
        elif idx in (11, 12):
            check_order_pending_history(page, "자동화규칙_묶음", product, "승인 요청", False, True)
        else:
            continue
        page.wait_for_timeout(3000)
    
    
