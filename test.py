import random
from config import URLS, Account
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login

def test_stock_inflow(page):
    bay_login(page)

    product_name = "제품 2000"
    quantity = 1
    memo = "30자까지 제한인데요. 최대글자수 꽉꽉채워서 등록합니다."

    page.goto(URLS["bay_stock"])
    for i in range(1):  # 반복
        page.click("data-testid=btn_stockadd")
        page.wait_for_url(URLS["bay_stockadd"])

        # 상태 드롭다운 옵션 클릭
        page.locator("data-testid=drop_status_trigger").click()
        page.get_by_role("option", name="입고", exact=True).click()

        # 제품명 드롭다운 옵션이 보일 때까지 기다리기
        page.locator("data-testid=drop_prdname_trigger").click()
        page.locator("data-testid=drop_prdname_item").wait_for(state="visible")

        # 제품명 옵션 확인
        options = page.locator("data-testid=drop_prdname_item").all_inner_texts()

        # 제품명이 정확히 일치하는 옵션 클릭
        page.get_by_role("option", name=product_name, exact=True).wait_for(state="attached")
        page.get_by_role("option", name=product_name, exact=True).click()


        page.fill("data-testid=input_qty", str(quantity))

        # ✅ placeholder 기반으로 메모 필드 찾기
        memo_input = page.get_by_placeholder("최대 30자 입력")
        memo_input.fill(memo)


        page.locator("data-testid=btn_save").click()
        page.wait_for_timeout(1000)

