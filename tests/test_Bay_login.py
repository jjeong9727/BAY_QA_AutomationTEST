import pytest
import requests
from playwright.sync_api import sync_playwright
from config import URLS, Account

# 로그인 테스트 
def test_login_wrong_password(page):

    page.goto(URLS["bay_login"])
    page.wait_for_timeout(2000)

    try:
        # 1. 로그인 버튼이 비활성화되어 있는지 확인
        login_button = page.locator("data-testid=btn_login")
        assert login_button.is_disabled(), "[FAIL] 로그인 버튼이 비활성화되지 않았습니다."

        # 2. 아이디와 비밀번호를 입력
        page.fill("data-testid=input_id", Account["testid"])
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_pw", Account["wrongpw"])  # 잘못된 비밀번호 입력
        page.wait_for_timeout(1000)

        # 3. 로그인 버튼 클릭
        login_button.click()
        page.wait_for_timeout(1000)

        # 4. "이메일 또는 비밀번호가 올바르지 않습니다" 문구가 나타나는지 확인
        locator = page.locator("data-testid=alert_wrong_pw")
        locator.wait_for(state="visible", timeout=5000)
        assert locator.is_visible(), "[FAIL] 이메일 또는 비밀번호가 올바르지 않습니다 문구가 보이지 않습니다."

        print("[PASS] 비밀번호 불일치 테스트 성공")

        # 아이디, 비밀번호 입력 후 로그인 버튼 클릭
        page.fill("data-testid=input_id", Account["testid"])  # 아이디 입력
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_pw", Account["testpw"])  # 비밀번호 입력
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_login", timeout=50000)  # 로그인 버튼 클릭
        page.wait_for_timeout(1000)

        print("[PASS] 로그인 테스트 성공")

    except Exception as e:
        error_message = f"❌ 비밀번호 불일치 테스트 실패! 오류: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise
