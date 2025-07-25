import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.order_status_utils import search_order_history
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
import time


def get_next_10min_slot() -> datetime:
    now = datetime.now()
    minute = (now.minute // 10 + 1) * 10
    if minute == 60:
        next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        next_time = now.replace(minute=minute, second=0, microsecond=0)
    return next_time

def wait_until(target_time: datetime):
    print(f"⏳ 다음 발주 배치 시각까지 대기 중: {target_time.strftime('%H:%M')}")
    while True:
        now = datetime.now()
        remaining = (target_time - now).total_seconds()
        if remaining <= 0:
            print("✅ 도달 완료! 발주 내역 확인 시작")
            break
        elif remaining > 60:
            print(f"🕒 {int(remaining)}초 남음... 60초 대기")
            time.sleep(60)
        else:
            print(f"🕒 {int(remaining)}초 남음... {int(remaining)}초 대기")
            time.sleep(remaining)

def test_inflow (page:Page):
    bay_login(page)

    product_list = [
        "자동화제품_1",
        "자동화제품_2",
        "자동화제품_3",
    ]
    stock_manager = StockManager(page)
    for product in product_list:
        print(product)
        stock_manager.product_name = product

        inflow_qty = 10  
        stock_manager.perform_inflow(inflow_qty)

# 가장 가까운 시간으로 발주 규칙 변경 필요

    
def test_outflow(page:Page):
    bay_login(page)
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=stockadd").click()
    page.wait_for_timeout(2000)
    product_list = [f"자동화제품_{i}" for i in range(1, 10)]  # 1~9번 제품 리스트 생성
    outflow_qty = 5  # 예: 출고 수량 설정

    stock_manager = StockManager(page)

    for idx, product in enumerate(product_list):
        page.locator("data-testid=drop_status_trigger").click()
        page.wait_for_timeout(1000)
        page.get_by_role("option", name="출고", exact=True).click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_qty").fill(str(outflow_qty))
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_memo").fill(f"{product} 제품 출고")
        page.wait_for_timeout(1000)

        if idx < len(product_list) - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)

    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_search").fill(product)
    page.locator("data-testid=history").is_hidden(timeout=3000)

    next_time = get_next_10min_slot()
    wait_until(next_time)

    page.reload()
    page.wait_for_timeout(1000)
    search_order_history(page, "자동화제품_3", "발주 요청")
    cell_locator = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=1")
    expect(cell_locator).to_have_text("자동화제품_1 외 2건", timeout=3000)

    page.locator("data-testid=input_search").fill("자동화제품_6")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    cell_locator = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=1")
    expect(cell_locator).to_have_text("자동화제품_4 외 2건", timeout=3000)

    page.locator("data-testid=input_search").fill("자동화제품_9")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    cell_locator = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=1")
    expect(cell_locator).to_have_text("자동화제품_7 외 2건", timeout=3000)
    page.wait_for_timeout(1000)   