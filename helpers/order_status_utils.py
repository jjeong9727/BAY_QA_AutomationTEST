import json
from playwright.sync_api import Page

def load_products_from_json():
    with open("product_name.json", "r", encoding="utf-8") as f:
        return json.load(f)

def filter_products_by_delivery_status(delivery_status: int):
    # 제품 파일에서 배송 상태에 맞는 제품만 필터링하여 반환
    products = load_products_from_json()
    filtered_products = [product for product in products if product.get("delivery_status") == delivery_status]
    return filtered_products

def get_product_by_name(product_name: str):
    # 제품명으로 특정 제품을 찾음
    products = load_products_from_json()
    for product in products:
        if product["kor"] == product_name:
            return product
    return None

def get_order_id_from_order_list(page: Page, product_name: str):
    # 발주 내역에서 제품명을 검색하여 해당 행의 order_id를 가져옴
    page.locator("data-testid=input_search").fill(product_name)  # 제품명 검색
    page.click("data-testid=btn_search")  # 검색 버튼 클릭
    page.wait_for_timeout(2000)  # 검색 결과 대기

    # 검색 결과에서 order_id 가져오기
    rows = page.locator("table tbody tr").all()
    for row in rows:
        # 해당 행에서 제품명이 일치하는지 확인
        row_product_name = row.locator("td").nth(1).inner_text().strip()  # 제품명 열
        if row_product_name == product_name:
            # 제품명이 일치하면 해당 행에서 order_id 추출
            order_id = row.locator("[data-testid=order_id]").inner_text().strip()
            return order_id

    # 만약 해당 제품이 없으면 None 반환
    return None

def update_product_delivery_status(product_name: str, new_status: int):
    products = load_products_from_json()
    for product in products:
        if product["kor"] == product_name:
            product["delivery_status"] = new_status
            break
    
    # 변경된 데이터를 다시 product_name.json에 저장
    with open("product_name.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def check_order_status_by_order_id(page: Page, status_name: str, order_id: str, expected: dict):
    # 각 order_id에 대해 상태를 확인
    tables = page.locator("section").all()
    found = False
    
    for table in tables:
        rows = table.locator("table tbody tr").all()
        for row in rows:
            status = row.locator("td").nth(0).inner_text().strip()
            if status == status_name:
                current_order_id = row.locator("[data-testid=order_id]").inner_text().strip()
                if current_order_id == order_id:
                    found = True
                    # 상태별 조건 확인
                    for key, value in expected.items():
                        if key == "resend_enabled":
                            assert row.locator("[data-testid=btn_resend]").is_enabled() == value
                        if key == "tracking_text":
                            assert value in row.locator("td").nth(8).inner_text().strip()
                        if key == "receive_enabled":
                            assert row.locator("[data-testid=btn_receive]").is_enabled() == value
                        if key == "cancel_enabled":
                            assert row.locator("[data-testid=btn_cancel]").is_enabled() == value
                    break
        if found:
            break

    if not found:
        raise AssertionError(f"발주 내역을 찾을 수 없습니다: {status_name}, {order_id}")
