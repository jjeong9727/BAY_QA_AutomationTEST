import json
import random
from playwright.sync_api import Page, sync_playwright
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id,
)
from helpers.order_status_data import order_status_map


def update_product_status_in_json(product_name: str, delivery_status: int):
    try:
        with open("product_name.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        for product in products:
            if product["kor"] == product_name:
                product["delivery_status"] = delivery_status
                break

        with open("product_name.json", "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    except Exception as e:
        raise RuntimeError(f"Error updating product status in JSON: {str(e)}")


def test_order_delivery(page: Page):
    try:
        # delivery_status가 2인 제품 선택
        with open("product_name.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        eligible_products = [p for p in products if p.get("delivery_status") == 2]
        if not eligible_products:
            raise ValueError("No product found with delivery_status 2")

        target_product = random.choice(eligible_products)
        product_name = target_product["kor"]


        # 로그인
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_timeout(1000)

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 발주 상태 확인: '발주 진행'
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        # 배송 URL 진입
        tracking_url = f"{URLS["base_accept_url"]}/{order_id}/delivery"
        page.goto(tracking_url)

        # 본인 인증
        page.fill("input[data-testid='input_name']", "김사라")
        page.fill("input[data-testid='input_contact']", "01098796020")
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(1000)

        # 배송사 선택 드롭다운 열기
        page.locator("data-testid=drop_shipping_trigger").click()
        options = page.locator("div[data-testid='drop_shipping_item'] div[role='option']")
        target = options.nth(1)
        carrier_name = target.inner_text().strip()
        print(f"[INFO] 선택된 배송사: {carrier_name}")

        # 항목 클릭
        target.click()


        # 이후 페이지 이동 후 해당 값 활용 예시
        print(f"[INFO] 선택한 택배사: {carrier_name}")


        page.fill("input[data-testid='input_tracking']", "1234567890")
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(5000)

        # 상태 확인: 배송 진행
        page.goto(URLS["bay_orderList"])
        page.fill("data-testid=input_search", product_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "배송 진행", f"[FAIL] {product_name} 상태가 '배송 진행'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 배송 진행 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # JSON 상태 업데이트
        update_product_status_in_json(product_name, delivery_status=3)

    except Exception as e:
        print(f"❌ Error in test_order_delivery: {str(e)}")
        raise


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        test_order_delivery(page)
        browser.close()


if __name__ == "__main__":
    main()
