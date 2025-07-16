import json
from pathlib import Path
from config import URLS
from datetime import datetime
from playwright.sync_api import Page, expect
from helpers.product_utils import update_product_flag
def register_stock_for_date(
    page: Page,
    date: datetime,
    product_name: str,
    current_stock: int,
    past_memo: str
):
    page.click("data-testid=btn_stockadd")
    page.wait_for_timeout(2000)
    # 날짜 포맷
    mmd = date.strftime("%m%d")  # MMDD → 버튼 testid용
    ymd = date.strftime("%Y. %m. %d")  # 텍스트 비교용
    txt_register = f"해당 날짜로 재고 등록하시겠습니까?"

    # 날짜 선택
    page.locator("[data-testid=select_date]").click()
    page.wait_for_timeout(1000)
    page.locator(f"[data-testid=btn_day_{mmd}]").click()
    page.wait_for_timeout(1000)

    # 입고 상태 선택
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name="입고", exact=True).click()
    page.wait_for_timeout(1000)

    # 제품명 선택
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_prdname_search", product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item", has_text=product_name).click()

    # 현재 재고 확인
    stock=current_stock
    expect(page.locator("data-testid=txt_current_stock")).to_have_text(str(stock), timeout=3000)

    # 입고 수량 입력 및 저장
    instock = 100
    page.fill("data-testid=input_qty", str(instock))
    page.wait_for_timeout(500)

    expected = int(stock) + instock
    page.fill("data-testid=input_memo", past_memo)
    page.wait_for_timeout(500)

    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_register")).to_have_text(txt_register, timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # JSON 파일 갱신
    update_product_flag(product_name, stock_qty=expected)

class StockManager:
    def __init__(self, page):
        self.page = page
        self.product_file_path = "product_name.json"  # product_file_path 속성 정의
        self.product_name = ""  # 제품명 속성 정의

    def load_product_from_json(self):
        """제품 정보를 JSON 파일에서 로드"""
        try:
            with open(self.product_file_path, "r", encoding="utf-8") as f:
                self.products = json.load(f)  # JSON 파일에서 제품 정보 로드
            return self.products
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {self.product_file_path}")
        except Exception as e:
            print(f"❌ 파일을 로드하는 중 오류 발생: {str(e)}")
            return []

    def get_all_product_names(self):
        if not hasattr(self,  "products"):
            self.load_product_from_json()
        return self.products

    def search_product_by_name(self, product_name):
        self.product_name = product_name  # 제품명 저장
        # 'product_name'을 기준으로 검색을 실행
        self.page.goto(URLS["bay_prdList"])
        self.page.fill("[data-testid='input_search']", self.product_name)
        self.page.click("[data-testid='btn_search']")
        self.page.wait_for_selector(f"text={self.product_name}")  # 제품이 검색 결과에 나타날 때까지 기다림
        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            # 제품명이 포함된 컬럼 인덱스 수정 필요
            if self.product_name in columns[3]:  # 컬럼 인덱스를 맞춰주세요
                stock_value = columns[6].strip()
                self.initial_stock = int(stock_value) if stock_value.isdigit() else 0
                return self.initial_stock
        raise Exception(f"{self.product_name} 제품을 찾을 수 없습니다.")
    def get_current_stock(self):
        self.page.goto(URLS["bay_prdList"])
        self.page.wait_for_timeout(2000)
        self.page.fill("data-testid=input_search", self.product_name)
        self.page.wait_for_timeout(500)
        self.page.locator("data-testid=btn_search").click()
        self.page.wait_for_timeout(2000)  # 충분한 대기 시간 추가

        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            
            
            # 제품명에서 줄바꿈 기준으로 첫 번째 값(한글)을 추출하여 비교
            korean_product_name = columns[3].split('\n')[0].strip()  # 줄바꿈 기준으로 첫 번째 값 추출
            print(f"현 재고: {self.product_name}, 노출 값: {korean_product_name}")
            if korean_product_name == self.product_name.strip():
                stock_value = columns[6].strip()  # 재고량 확인 (7열)
                return int(stock_value) if stock_value.isdigit() else 0
        
        raise Exception(f"재고 확인 실패: {self.product_name}")
    

    


    def perform_inflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.wait_for_timeout(2000)
        self.page.click("data-testid=btn_stockadd")
        self.page.wait_for_timeout(2000)
        self.page.wait_for_url(URLS["bay_stockadd"])
        self.page.wait_for_timeout(1000)
        
        # 상태 드롭다운 옵션 클릭
        self.page.locator("data-testid=drop_status_trigger").click()
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("option", name="입고", exact=True).click()

        # 제품명선택 
        self.page.locator("data-testid=drop_prdname_trigger").click()
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=drop_prdname_search").fill(self.product_name)
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=drop_prdname_item", has_text=self.product_name).click()
        self.page.wait_for_timeout(1000)
        
        self.page.fill("data-testid=input_qty", str(quantity))
        self.page.wait_for_timeout(1000)
        self.page.fill("data-testid=input_memo", "30자까지 제한인데요. 최대글자수 꽉꽉채워서 등록합니다.")
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=btn_save").click()
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=btn_confirm").click()
        self.page.wait_for_timeout(3000)

    def perform_outflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.wait_for_timeout(2000)
        self.page.click("data-testid=btn_stockadd")
        self.page.wait_for_timeout(2000)
        self.page.wait_for_url(URLS["bay_stockadd"])
        self.page.wait_for_timeout(1000)

        self.page.locator("data-testid=drop_status_trigger").click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name="출고", exact=True).click()
        self.page.wait_for_timeout(500)
        # 제품명선택 
        self.page.locator("data-testid=drop_prdname_trigger").click()
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=drop_prdname_search").fill(self.product_name)
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=drop_prdname_item", has_text=self.product_name).click()
        self.page.wait_for_timeout(1000)
        self.page.fill("data-testid=input_qty", str(quantity))
        self.page.wait_for_timeout(500)
        memo_input = self.page.get_by_placeholder("최대 30자 입력")
        memo_input.fill("30자까지 제한인데요. 최대글자수 꽉꽉채워서 등록합니다.")
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=btn_save").click()
        self.page.wait_for_timeout(1000)
        self.page.locator("data-testid=btn_confirm").click()
        self.page.wait_for_timeout(3000)