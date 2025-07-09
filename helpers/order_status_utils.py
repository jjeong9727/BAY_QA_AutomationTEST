import json
from playwright.sync_api import Page, expect

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
    first_table = page.locator("table").first  # 첫 번째 테이블만 선택
    rows = first_table.locator("tbody tr").all()  # 첫 번째 테이블의 모든 행을 가져옴

    for row in rows:
        # 해당 행에서 제품명이 일치하는지 확인
        row_product_locator = row.locator("td").nth(1).locator("p")
        row_product_name = row_product_locator.inner_text().strip()
        print(f"🔍 검색된 제품명: {row_product_name}")

        # 제품명이 일치하는지 비교
        if row_product_name == product_name:
            # 제품명이 일치하면 해당 행에서 order_id 추출
            order_id = row.locator("td[data-testid='order']").get_attribute('data-orderid')
            print(f"✅ 찾은 order_id: {order_id}")
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

from playwright.sync_api import expect

def check_order_status_by_order_id(page: Page, status_name: str, order_id: str, expected: dict):
    histories = page.locator("[data-testid='history']").all()
    found = False

    for history in histories:
        table = history.locator("table")
        rows = table.locator("tbody tr").all()
        
        for row in rows:
            status = row.locator("td").nth(0).inner_text().strip()
            order_data_id = row.locator("td[data-testid='order']").get_attribute('data-orderid')

            print(f"상태: {status}")
            print(f"주문 ID: {order_data_id}")
            
            if status == status_name and order_data_id == order_id:
                found = True

                for key, value in expected.items():
                    if key == "resend_enabled":
                        resend_button = row.locator("[data-testid=btn_resend]")
                        if value:
                            expect(resend_button).to_be_enabled()
                        else:
                            expect(resend_button).to_be_disabled()

                    if key == "tracking_text":
                        td_tracking = row.locator("td").nth(7)
                        text = td_tracking.text_content().strip()
                        print(f"[디버깅] 운송장 텍스트: '{text}'")
                        assert value in text, f"운송장 칸에 '{value}'가 없음. 실제 값: '{text}'"

                    if key == "tracking_enabled":
                        td_tracking = row.locator("td").nth(7)
                        tracking_button = td_tracking.locator("[data-testid=btn_check_tracking]")
                        if tracking_button.count() > 0:
                            if value:
                                expect(tracking_button).to_be_enabled()
                            else:
                                expect(tracking_button).to_be_disabled()
                        else:
                            assert not value, "트래킹 버튼이 없지만 활성화를 기대하고 있습니다."

                    if key == "receive_enabled":
                        receive_button = row.locator("[data-testid=btn_receive]")
                        if value:
                            expect(receive_button).to_be_enabled()
                        else:
                            expect(receive_button).to_be_disabled()

                    if key == "cancel_enabled":
                        cancel_button = row.locator("[data-testid=btn_cancel]")
                        if value:
                            expect(cancel_button).to_be_enabled()
                        else:
                            expect(cancel_button).to_be_disabled()

                break

        if found:
            break

    if not found:
        raise AssertionError(f"발주 내역을 찾을 수 없습니다: {status_name}, {order_id}")


