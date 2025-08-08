import json
import re
import random
from playwright.sync_api import Page, sync_playwright, expect 
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status,
    get_order_id_from_order_list,
    check_order_status_by_order_id,
    search_order_history
)
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login


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
        status_name = "발주 진행"
        supplier = target_product['supplier']
        match = re.search(r",\s*(.*?)\s+(\d{3}-\d{4}-\d{4})", supplier)
        if match:
            name = match.group(1)
            phone = match.group(2)
        else:
            name = ""
            phone = ""

        # 로그인
        bay_login(page)

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        search_order_history(page, product_name, status_name)

        # # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 발주 상태 확인: '발주 진행'
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        # 배송 URL 진입
        tracking_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)

        # 본인 인증
        page.fill("input[data-testid='input_name']", name)
        page.fill("input[data-testid='input_contact']", phone)
        page.click("button[data-testid='btn_confirm']")
        expect(page.locator("data-testid=drop_shipping_trigger")).to_be_visible(timeout=5000)

        # 배송사 선택 드롭다운 열기
        carrier_name = "일양로지스"
        tracking = "1234567890"
        new_carrier = "CJ대한통운"
        new_tracking = "0987654321"
        page.locator("data-testid=drop_shipping_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_search").fill(carrier_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_item", has_text=carrier_name).click()
        page.wait_for_timeout(1000)
        
        page.fill("input[data-testid='input_tracking']", tracking)
        page.wait_for_timeout(3000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        expect(page.locator("data-testid=toast_tracking")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        # 상태 확인: 배송 진행
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(500)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(500)

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
        
        # JSON 상태 업데이트
        update_product_status_in_json(product_name, delivery_status=3)

        # 택배사 + 운송장 확인
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(2000)
        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(carrier_name, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text(tracking, timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        # 운송정보 수정 후 확인
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_name']", name)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", phone)
        page.wait_for_timeout(1000)
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(1000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_search").fill(new_carrier)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_item", has_text=new_carrier).click()
        page.wait_for_timeout(1000)
        
        page.fill("input[data-testid='input_tracking']", new_tracking)
        page.wait_for_timeout(3000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        bay_login(page)
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(2000)

        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(new_carrier, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text(new_tracking, timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")



    except Exception as e:
        print(f"❌ Error in test_order_delivery: {str(e)}")
        raise


def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False)

        test_order_delivery(page)
        page.close()


if __name__ == "__main__":
    main()
