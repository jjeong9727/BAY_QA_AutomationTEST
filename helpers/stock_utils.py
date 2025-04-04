import json
from pathlib import Path
from config import URLS


class StockManager:
    def __init__(self, page):
        self.page = page
        self.original_product_name = ""
        self.display_product_name = ""
        self.initial_stock = 0

    def load_product_from_json(self):
        json_path = Path("product_name.json")
        if not json_path.exists():
            raise FileNotFoundError("product_name.json 파일이 존재하지 않습니다.")
        with open(json_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        if not products:
            raise ValueError("product 파일에 제품이 없습니다.")
        self.original_product_name = products[0]["kor"]
        self.display_product_name = products[0]["kor"]

    def search_product_by_name(self):
        # self.page.fill("data-testid=input_search", self.display_product_name)
        # self.page.click("data-testid=btn_search")
        self.page.goto(URLS["bay_prdList"])
        self.page.fill("input[placeholder='제품명 검색']", self.display_product_name)    
        self.page.locator("button:has-text('검색')").click()
        self.page.wait_for_timeout(1000)
        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            if self.original_product_name in columns[4]:
                stock_value = columns[6].strip()
                self.initial_stock = int(stock_value) if stock_value.isdigit() else 0
                return self.initial_stock
        raise Exception(f"{self.display_product_name} 제품을 찾을 수 없습니다.")

    def get_current_stock(self):
        self.page.goto(URLS["bay_prdList"])
        # self.page.fill("data-testid=input_search", self.display_product_name)
        # self.page.click("data-testid=btn_search")
        self.page.fill("input[placeholder='제품명 검색']", self.display_product_name)    
        self.page.locator("button:has-text('검색')").click()
        self.page.wait_for_timeout(1000)
        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            if self.original_product_name in columns[4]:
                stock_value = columns[6].strip()
                return int(stock_value) if stock_value.isdigit() else 0
        raise Exception(f"재고 확인 실패: {self.display_product_name}")

    def perform_inflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.click("data-testid=btn_stockAdd")
        self.page.wait_for_url(URLS["bay_stockAdd"])

        # self.page.locator("data-testid=drop_status").click()
        # self.page.get_by_role("option", name="입고", exact=True).click()
        # self.page.locator("data-testid=drop_prdname").click()
        # self.page.get_by_role("option", name=self.display_product_name, exact=True).click()
        # self.page.fill("data-testid=input_quantity", str(quantity))
        # self.page.click("data-testid=btn_save")
        
        self.page.locator("text=상태 선택").click()
        self.page.locator("text=입고").click()
        self.page.locator("text=제품명 선택").click()
        self.page.locator("text=마그네슘 정제").click()
        self.page.locator('[placeholder="0"]').last.fill("10")
        
        try:
            self.page.locator("text=저장").click()  # 저장 버튼 클릭
            # 페이지가 변경되었는지 확인 (예: 재고 목록으로 돌아갔다면 성공)
            self.page.wait_for_url(URLS["bay_stock"], timeout=5000)  # 5초 내로 페이지 전환 대기
            print("[PASS] 저장 버튼 클릭 성공")
        except Exception as e:
            print(f"[ERROR] 저장 버튼 클릭 실패: {e}")
            raise AssertionError("[ERROR] 저장 버튼 클릭 실패")  # 실패 시 명확한 에러 메시지 제공

        self.page.wait_for_url(URLS["bay_stock"])

        
        




    def perform_outflow(self, quantity: int):
        self.page.goto(URLS["bay_stock"])
        self.page.click("data-testid=btn_stockAdd")
        self.page.wait_for_url(URLS["bay_stockAdd"])

        self.page.locator("data-testid=drop_status").click()
        self.page.get_by_role("option", name="출고", exact=True).click()
        self.page.locator("data-testid=drop_prdname").click()
        self.page.get_by_role("option", name=self.display_product_name, exact=True).click()
        self.page.fill("data-testid=input_quantity", str(quantity))
        self.page.click("data-testid=btn_save")
        self.page.wait_for_url(URLS["bay_stock"])
