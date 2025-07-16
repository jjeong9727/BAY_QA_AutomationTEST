import json
import os
import pytest
import requests
from playwright.sync_api import sync_playwright, expect
from config import URLS, Account
file_path = os.path.join(os.path.dirname(__file__), "version_info.json")
# 로그인 테스트 
def test_login_wrong_password(page):

    page.goto(URLS["bay_login"])
    page.wait_for_timeout(2000)

    try:
        # 1. 로그인 버튼
        login_button = page.locator("data-testid=btn_login")

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
        page.click("data-testid=btn_login")  # 로그인 버튼 클릭
        expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=5000)
        page.wait_for_timeout(1000)
        print("[PASS] 로그인 테스트 성공")

        # 테스트 버전 가져오기
        version_span = page.locator("text=메디솔브에이아이(주)").locator("xpath=following-sibling::span")
        version_text = version_span.text_content().strip().splitlines()[-1].strip().strip('"')

        print(f"버전: {version_text}")

        version_data = {
            "version": version_text
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"version": version_text}, f, ensure_ascii=False, indent=2)



    except Exception as e:
        error_message = f"❌ 비밀번호 불일치 테스트 실패! 오류: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise
