from config import URLS, Account

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
            product_name = row.locator("td").nth(2).inner_text().strip()

            resend_btn = row.locator("[data-testid=btn_resend]")
            tracking_cell = row.locator("td").nth(8)
            tracking_btn = row.locator("[data-testid=btn_tracking]")
            receive_btn = row.locator("[data-testid=btn_receive]")
            cancel_btn = row.locator("[data-testid=btn_cancel]")

            if "resend_enabled" in expected:
                assert resend_btn.is_enabled() == expected["resend_enabled"]

            if "tracking_text" in expected:
                assert expected["tracking_text"] in tracking_cell.inner_text().strip()

            if "tracking_button" in expected:
                assert tracking_btn.is_visible()

            if "receive_enabled" in expected:
                assert receive_btn.is_enabled() == expected["receive_enabled"]

            if "receive_done_text" in expected:
                assert expected["receive_done_text"] in receive_btn.inner_text().strip()

            if "cancel_enabled" in expected:
                assert cancel_btn.is_enabled() == expected["cancel_enabled"]

            if resend_btn.is_enabled():
                resend_btn.click()
                page.locator("[data-testid=btn_confirm]").click()

            if tracking_btn.is_visible():
                with page.expect_popup() as popup_info:
                    tracking_btn.click()
                popup = popup_info.value
                popup.wait_for_load_state()
                assert "https://www.google.com" in popup.url
                popup.close()

            if receive_btn.is_enabled():
                receive_btn.click()
                page.locator("[data-testid=btn_confirm]").click()
                page.wait_for_timeout(1000)
                updated_btn_text = row.locator("[data-testid=btn_receive]").inner_text().strip()
                assert "수령 완료" in updated_btn_text

            if cancel_btn.is_enabled():
                cancel_btn.click()
                page.locator("[data-testid=btn_confirm]").click()
                page.wait_for_timeout(1000)
                updated_status = row.locator("td").nth(0).inner_text().strip()
                assert updated_status == "발주 취소"

            break
        if found:
            break

    assert found, f"상태 '{status_name}' 행을 찾을 수 없음"
