from config import URLS, Account
from helpers.product_utils import get_product_stock, update_product_flag

def check_order_status(browser, status_name, expected):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_orderList"])
    page.wait_for_url(URLS["bay_orderList"], timeout=60000)

    page.locator("data-testid=drop_status").click()
    options = page.locator("[data-testid^=drop_status_item]").all()
    for option in options:
        if option.inner_text().strip() == status_name:
            option.click()
            break

    page.click("data-testid=btn_search")
    page.wait_for_timeout(2000)

    tables = page.locator("section").all()
    found = False

    for table in tables:
        rows = table.locator("table tbody tr").all()
        for row in rows:
            status = row.locator("td").nth(0).inner_text().strip()
            if status != status_name:
                continue

            found = True
            product_name = row.locator("td").nth(1).inner_text().strip()
            order_qty_text = row.locator("td").nth(3).inner_text().strip()
            order_qty = int(order_qty_text) if order_qty_text.isdigit() else 0

            resend_btn = row.locator("[data-testid=btn_resend]")
            tracking_cell = row.locator("td").nth(8)
            tracking_btn = row.locator("[data-testid=btn_tracking]")
            receive_btn = row.locator("[data-testid=btn_receive]")
            cancel_btn = row.locator("[data-testid=btn_cancel]")

            try:
                if "resend_enabled" in expected:
                    assert resend_btn.is_enabled() == expected["resend_enabled"]
            except Exception as e:
                print(f"[ERROR] 재발송 버튼 상태 확인 실패: {product_name}\n{e}")

            try:
                if "tracking_text" in expected:
                    assert expected["tracking_text"] in tracking_cell.inner_text().strip()
                if "tracking_button" in expected:
                    assert tracking_btn.is_visible()
            except Exception as e:
                print(f"[ERROR] 배송조회 요소 확인 실패: {product_name}\n{e}")

            try:
                if "receive_enabled" in expected:
                    assert receive_btn.is_enabled() == expected["receive_enabled"]
                if "receive_done_text" in expected:
                    assert expected["receive_done_text"] in receive_btn.inner_text().strip()
            except Exception as e:
                print(f"[ERROR] 수령확정 버튼 상태 확인 실패: {product_name}\n{e}")

            try:
                if "cancel_enabled" in expected:
                    assert cancel_btn.is_enabled() == expected["cancel_enabled"]
            except Exception as e:
                print(f"[ERROR] 취소 버튼 상태 확인 실패: {product_name}\n{e}")

            try:
                if resend_btn.is_enabled():
                    resend_btn.click()
                    page.locator("[data-testid=btn_confirm]").click()
            except Exception as e:
                print(f"[ERROR] 재발송 처리 실패: {product_name}\n{e}")

            try:
                if tracking_btn.is_visible():
                    with page.expect_popup() as popup_info:
                        tracking_btn.click()
                    popup = popup_info.value
                    popup.wait_for_load_state()
                    assert "https://www.google.com" in popup.url # 테스트용 구글 주소 (추후 변동 예정) 링크 생성 방법? 문의 후 테스트 방법 확정 필요요
                    popup.close()
            except Exception as e:
                print(f"[ERROR] 배송조회 처리 실패: {product_name}\n{e}")

            try:
                if receive_btn.is_enabled():
                    before_stock = get_product_stock(page, product_name)
                    receive_btn.click()
                    page.locator("[data-testid=btn_confirm]").click()
                    page.wait_for_timeout(1000)

                    updated_btn_text = row.locator("[data-testid=btn_receive]").inner_text().strip()
                    assert "수령 완료" in updated_btn_text

                    after_stock = get_product_stock(page, product_name)
                    expected_stock = before_stock + order_qty

                    assert after_stock == expected_stock, (
                        f"[FAIL] 자동 입고 실패 : 예상 {expected_stock}, 실제 {after_stock}"
                    )

                    update_product_flag(product_name, order_flag=False)
                    print(f"[PASS] 수령 확정 후 자동 입고 확인 완료 : {product_name} (입고 {order_qty}개)")
            except Exception as e:
                print(f"[ERROR] 수령확정 처리 실패: {product_name}\n{e}")

            try:
                if cancel_btn.is_enabled():
                    cancel_btn.click()
                    page.locator("[data-testid=btn_confirm]").click()
                    page.wait_for_timeout(1000)

                    updated_status = row.locator("td").nth(0).inner_text().strip()
                    assert updated_status == "발주 취소"
            except Exception as e:
                print(f"[ERROR] 취소 처리 실패: {product_name}\n{e}")

            break
        if found:
            break

    assert found, f"상태 '{status_name}' 행을 찾을 수 없음"
