import pytest
import random
from playwright.sync_api import Page
from config import URLS, Account
import requests

SLACK_WEBHOOK_URL = URLS["slack_PV"]

def send_slack_message(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    assert response.status_code == 200, "❌ Slack 메시지 전송 실패!"

class TestProductCategoryValidation:

    def login(self, page: Page):
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])

    def go_to_product_add(self, page: Page):
        page.goto(URLS["bay_prdAdd"])
        page.wait_for_timeout(1000)

    def assert_duplicate_alert(self, page: Page, testid: str, pass_msg: str, fail_context: str):
        try:
            alert = page.locator(f'[data-testid="{testid}"]')
            assert alert.is_visible(), f"[FAIL][제품관리] {fail_context} 중복 경고 미표시"
            msg = f"[PASS][제품등록] Validation {fail_context} 중복 테스트"
            print(msg)
            send_slack_message(msg)
        except Exception as e:
            fail_msg = f"[FAIL][제품등록] Validation {fail_context} 중복 테스트 실패\n에러: {str(e)}"
            print(fail_msg)
            send_slack_message(fail_msg)
            raise

    def test_duplicate_type_name(self, browser):
        page = browser.new_page()
        self.login(page)
        self.go_to_product_add(page)

        page.fill("data-testid=input_type", "중복 테스트 타입")
        page.click("data-testid=btn_save")
        page.wait_for_timeout(1000)

        self.assert_duplicate_alert(page, "alert_dup_type", "타입", "타입")

    def test_duplicate_category_name(self, browser):
        page = browser.new_page()
        self.login(page)
        self.go_to_product_add(page)

        page.fill("data-testid=input_ctg", "중복 테스트 종류")
        page.click("data-testid=btn_save")
        page.wait_for_timeout(1000)

        self.assert_duplicate_alert(page, "alert_dup_ctg", "종류", "종류")

    def test_duplicate_maker_name(self, browser):
        page = browser.new_page()
        self.login(page)
        self.go_to_product_add(page)

        page.fill("data-testid=input_maker", "중복 테스트 제조사")
        page.click("data-testid=btn_save")
        page.wait_for_timeout(1000)

        self.assert_duplicate_alert(page, "alert_dup_maker", "제조사", "제조사")
