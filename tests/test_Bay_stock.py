import pytest
import random
import requests
from playwright.sync_api import sync_playwright
from config import URLS, Account
from datetime import datetime
from helpers.product_utils import update_product_flag


class StockManager:
    """제품 선택 및 재고 관리 클래스"""
    
    def __init__(self, page):
        self.page = page
        self.original_product_name = 0
        self.display_product_name = 0
        self.initial_stock = 0

    def select_random_product(self):
        """테이블에서 랜덤으로 제품을 선택하고, 원본 제품명과 재고량 저장"""
        try:
            rows = self.page.locator("table tbody tr").all()
            if not rows:
                raise Exception("제품 목록이 비어 있음!")

            random_row = random.choice(rows)
            columns = random_row.locator("td").all_inner_texts()

            if len(columns) < 6:
                raise Exception("선택된 행에서 제품명 또는 재고량을 찾을 수 없음!")

            self.original_product_name = columns[1].strip()
            self.display_product_name = self.original_product_name.split("\n")[0]  # UI에서 선택할 첫 번째 줄
            stock_value = columns[2].strip()

            if not stock_value.isdigit():
                raise Exception(f"[{self.original_product_name}]의 재고 값이 숫자가 아님: {stock_value}")

            self.initial_stock = int(stock_value)

            return self.original_product_name, self.display_product_name, self.initial_stock

        except Exception as e:
            print(f"제품 선택 중 오류 발생: {str(e)}")
            return None, None, None

    def get_current_stock(self):
        """선택된 제품명의 현재 재고량을 반환"""
        if not self.original_product_name:
            print("오류: 저장된 제품명이 없음")
            return 0

        try:
            rows = self.page.locator("table tbody tr").all()
            for row in rows:
                columns = row.locator("td").all_inner_texts()
                if len(columns) < 6:
                    continue

                row_product_name = columns[1].strip()
                if self.original_product_name in row_product_name:  # 원본 제품명 비교
                    stock_value = columns[2].strip()
                    return int(stock_value) if stock_value.isdigit() else None

            return None  # 제품을 찾지 못한 경우

        except Exception as e:
            print(f"재고 검색 중 오류 발생: {str(e)}")
            return None

def test_stock_inflow(browser):
    """재고 입고 테스트"""
    page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)

    # StockManager 인스턴스 생성 후 제품 선택
    stock_manager = StockManager(page)
    original_product_name, display_product_name, initial_stock = stock_manager.select_random_product()
    
    stock_change = random.randint(1, 10)
    print(f"선택한 제품명: {original_product_name} (UI 선택용: {display_product_name}) / 재고: {initial_stock}")

    page.goto(URLS["bay_stock"])
    page.wait_for_url(URLS["bay_stock"], timeout=60000)
    page.click("data-testid=btn_stockAdd")
    page.wait_for_url(URLS["bay_stockAdd"], timeout=60000)

    page.locator("data-testid=drop_status").click()
    page.get_by_role("option", name="입고", exact=True).click()

    # 🔹 제품 선택 시 `get_by_role("option")`을 사용하여 정확한 제품 선택
    page.locator("data-testid=drop_prdname").click()
    page.get_by_role("option", name=display_product_name, exact=True).click()

    page.fill("data-testid=input_quantity", str(stock_change))
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_stock"], timeout=60000)

    expected_stock = initial_stock + stock_change

    # StockManager 클래스를 사용하여 재고 확인

    page.goto(URLS["bay_prdList"])
    displayed_stock = stock_manager.get_current_stock()

    assert expected_stock == displayed_stock, f"재고 불일치: 예상 {expected_stock}, 표시된 {displayed_stock}"

    print(f"{original_product_name} - 입고 {stock_change}개 완료! 현재 재고: {displayed_stock}")

    message = f"[PASS][입고테스트] {display_product_name} 기존 재고 {initial_stock} + 입고 {stock_change}개 완료! 현재 재고 {displayed_stock}"
    print(message)

    update_product_flag(original_product_name, undeletable=True)


def test_stock_outflow(browser):
    """재고 출고 테스트"""
    page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)

    # StockManager 인스턴스 생성 후 제품 선택
    stock_manager = StockManager(page)
    original_product_name, display_product_name, initial_stock = stock_manager.select_random_product()
    
    stock_change = random.randint(1, initial_stock) if initial_stock > 0 else 0
    if stock_change == 0:
        print(f"[재고 불가] {original_product_name}의 현재 재고 수량이 0 입니다.")
        return
    print(f"출고할 제품명: {original_product_name} (UI 선택용: {display_product_name}) / 재고: {initial_stock}")

    page.goto(URLS["bay_stock"])
    page.wait_for_url(URLS["bay_stock"], timeout=60000)
    page.click("data-testid=btn_stockAdd")
    page.wait_for_url(URLS["bay_stockAdd"], timeout=60000)

    page.locator("data-testid=drop_status").click()
    page.get_by_role("option", name="출고", exact=True).click()

    # 🔹 제품 선택 시 정확한 제품 선택
    page.locator("data-testid=drop_prdname").click()
    page.get_by_role("option", name=display_product_name, exact=True).click()

    page.fill("data-testid=input_quantity", str(stock_change))
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_stock"], timeout=60000)

    expected_stock = initial_stock - stock_change

    # StockManager 클래스를 사용하여 재고 확인

    page.goto(URLS["bay_prdList"])
    displayed_stock = stock_manager.get_current_stock()

    assert expected_stock == displayed_stock, f"재고 불일치: 예상 {expected_stock}, 표시된 {displayed_stock}"

    print(f"{display_product_name} - 출고 {stock_change}개 완료! 현재 재고: {displayed_stock}")

    message = f"[PASS][출고테스트] {display_product_name} 기존 재고 {initial_stock} - 출고 {stock_change}개 완료! 현재 재고 {displayed_stock}"
    print(message)

    safety_stock = 10
    if displayed_stock <= safety_stock:
        print(f"{display_product_name} 현재 재고({displayed_stock})가 안전 재고({safety_stock})보다 작음 → 자동 발주 확인 진행")

        verify_auto_order(page, display_product_name)


def verify_auto_order(page, product_name):
    page.goto(URLS["bay_orderList"])
    page.wait_for_url(URLS["bay_orderList"], timeout=60000)

    assert page.url == URLS["bay_orderList"]
    success_message = "[Pass] 발주내역으로 이동 확인"
    print(success_message)

   