import json
from pathlib import Path
from config import URLS


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
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {self.product_file_path}")
        except Exception as e:
            print(f"❌ 파일을 로드하는 중 오류 발생: {str(e)}")

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
        self.page.fill("data-testid=input_search", self.product_name)
        self.page.locator("data-testid=btn_search").click()
        self.page.wait_for_timeout(2000)  # 충분한 대기 시간 추가

        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            
            
            # 제품명에서 줄바꿈 기준으로 첫 번째 값(한글)을 추출하여 비교
            korean_product_name = columns[3].split('\n')[0].strip()  # 줄바꿈 기준으로 첫 번째 값 추출
            if korean_product_name == self.product_name.strip():
                stock_value = columns[6].strip()  # 재고량 확인 (7열)
                return int(stock_value) if stock_value.isdigit() else 0
        
        raise Exception(f"재고 확인 실패: {self.product_name}")
    def perform_inflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.click("data-testid=btn_stockadd")
        self.page.wait_for_url(URLS["bay_stockadd"])

        # 상태 드롭다운 옵션 클릭
        self.page.locator("data-testid=drop_status_trigger").click()
        self.page.get_by_role("option", name="입고", exact=True).click()

        # 제품명 드롭다운 옵션이 보일 때까지 기다리기
        self.page.locator("data-testid=drop_prdname_trigger").click()
        self.page.locator("data-testid=drop_prdname_item").wait_for(state="visible")

        # 제품명 옵션 확인
        options = self.page.locator("data-testid=drop_prdname_item").all_inner_texts()

        # 제품명이 정확히 일치하는 옵션 클릭
        self.page.get_by_role("option", name=self.product_name, exact=True).wait_for(state="attached")
        self.page.get_by_role("option", name=self.product_name, exact=True).click()

        self.page.fill("data-testid=input_qty", str(quantity))
        self.page.locator("data-testid=btn_save").click()
        self.page.wait_for_timeout(1000)


        
        




    def perform_outflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.click("data-testid=btn_stockadd")
        self.page.wait_for_url(URLS["bay_stockadd"])

        self.page.locator("data-testid=drop_status_trigger").click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name="출고", exact=True).click()
        self.page.wait_for_timeout(500)
        self.page.locator("data-testid=drop_prdname_trigger").click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=self.product_name, exact=True).click()
        self.page.wait_for_timeout(500)
        self.page.fill("data-testid=input_qty", str(quantity))
        self.page.wait_for_timeout(500)
        self.page.click("data-testid=btn_save")
        self.page.wait_for_timeout(1000)
