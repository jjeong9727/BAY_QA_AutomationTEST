import random
import re
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.order_status_utils import search_order_history
from helpers.approve_utils import check_approval_history, check_order_pending_history
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
import time


# 수동 발주/승인 규칙O : "발주 예정 내역" 미노출, "발주 승인 요청 내역" 노출
# 수동 발주/승인 규칙X : "발주 예정 내역" 미노출, "발주 승인 요청 내역" 미노출
def test_stock_manual_order(page:Page):
    bay_login(page)
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)

    products = ["수동 발주 제품 1", "수동 발주 제품 2", "수동 발주 제품 3"]
    expected_rules = ["승인규칙_1명", "승인규칙_n명", "자동 승인"]
    price = "5000"
    quantity = "10"
    expected_amount = "50,000"
    expected_supplier = "자동화업체D, 권정의D 010-6275-4153"



    # 재고 가져오기 
        # 수동 발주 제품_1 
    page.locator("data-testid=input_search").fill(products[0])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock1 = stock_cell.inner_text()

        # 수동 발주 제품_2
    page.locator("data-testid=input_search").fill(products[1])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock2 = stock_cell.inner_text()

    # 수동 발주 제품_3
    page.locator("data-testid=input_search").fill(products[2])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator('table tbody tr')
    stock_cell = rows.nth(0).locator('td:nth-child(6)') #(재고관리 1행 6열)
    expected_stock3 = stock_cell.inner_text()

    expected_list = [expected_stock1, expected_stock2, expected_stock3]

    # 수동 발주 (수동 발주 제품_1, 2, 3)
    page.locator("data-testid=btn_order").click()
    page.wait_for_selector("data-testid=drop_prdname_trigger", timeout=10000)
    for idx, product in enumerate(products, start=1):
        page.locator("data-testid=drop_prdname_trigger").last.click()
        page.wait_for_selector("data-testid=drop_prdname_search", timeout=3000)
        page.locator("data-testid=drop_prdname_search").fill(product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_prdname_item", has_text=product).click()
        page.wait_for_timeout(1000)

        current_stock = page.locator("data-testid=txt_current_stock").last.input_value().strip()
        assert current_stock == expected_list[idx-1], f"재고가 일치하지 않음 (기대 값:{expected_list[idx-1]}, 노출 값: {current_stock})"
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_price").last.fill(price)
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_qty").last.fill(quantity)
        page.wait_for_timeout(1000)

        amount= page.locator("data-testid=txt_amount").last.input_value().strip()
        supplier = page.locator("data-testid=txt_supplier").last.input_value().strip()
        rule = page.locator("data-testid=txt_rule").last.input_value().strip()
        
        assert amount == expected_amount, f"발주 금액이 일치하지 않음 (기대 값:{expected_amount}, 노출 값: {amount})"
        assert supplier == expected_supplier, f"업체명이 일치하지 않음 (기대 값:{expected_supplier}, 노출 값: {supplier})"
        assert rule == expected_rules[idx-1], f"승인 규칙이 일치하지 않음 (기대 값:{expected_rules[idx-1]}, 노출 값: {rule})"

        if idx < len(products):
            page.locator("data-testid=btn_addrow").click()
            page.wait_for_timeout(1000) 
        
    # 저장 

    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("수동 발주를 진행하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=txt_amount").last).to_have_value(expected_amount, timeout=3000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("수동 발주를 진행하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_manual")).to_have_text("수동 발주가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)
        # 현재 시간 저장 (제품 별로)
    
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    
    # 승인 요청 내역 노출 확인 
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)
    check_approval_history(page, "승인 대기", products[0], auto=True, rule="수동 발주", time=now_str)
    check_approval_history(page, "승인 대기", products[1], auto=True, rule="수동 발주", time=now_str)
    check_approval_history(page, "승인 대기", products[2], auto=None) # 발주 내역 생성 확인 


    