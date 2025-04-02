import pytest
import requests
from playwright.sync_api import sync_playwright
from config import URLS, Account


# 정상 로그인 테스트
def test_login_success(browser):
    """아이디/비밀번호로 로그인 테스트 및 Slack 알림 전송"""
    page = browser.new_page()
    page.goto(URLS["bay_login"])  # 테스트 대상 URL

    # 아이디, 비밀번호 입력 후 로그인 버튼 클릭
    page.fill("data-testid=input_id", Account["testid"])  # 아이디 입력
    page.fill("data-testid=input_pw", Account["testpw"])  # 비밀번호 입력
    page.click("data-testid=btn_login", timeout=50000)  # 로그인 버튼 클릭

    try:
        # ✅ 로그인 버튼이 사라지는지 기다리기
        page.wait_for_selector("data-testid=btn_login", state="hidden", timeout=5000)

        # ✅ 로그인 성공 여부 확인
        assert page.url == URLS["bay_home"], "❌ 로그인 후 올바른 페이지로 이동하지 않음!"
        success_message = "[Pass] 정상 로그인 테스트"
        print(success_message)

    except Exception as e:
        error_message = f"❌ 로그인 실패! 오류: {str(e)}"
        print(error_message)
        raise



# 아이디/비밀번호 불일치 테스트
def test_login_wrong_password(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["wrongpw"])  # ❌ 잘못된 비밀번호 입력
    page.click("data-testid=btn_login")

    locator = page.locator("li[role='status']", has_text="이메일 또는 비밀번호가 올바르지 않습니다")
    locator.wait_for(state="visible", timeout=5000)
    assert locator.is_visible()
    print("[PASS] 비밀번호 불일치 테스트")

# 아이디/비밀번호 미입력 테스트
def test_login_empty_fields(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
        
    page.click("data-testid=btn_login")  # 빈 값으로 로그인 버튼 클릭
    # 🔹 오류 메시지가 나타날 때까지 최대 5초 대기
    assert "아이디을(를) 입력해주세요." in page.content()
    assert "비밀번호을(를) 입력해주세요." in page.content()

    # 필수 입력값 누락 메시지 확인
    success_msg = "[PASS] 로그인 미입력 테스트 "
    print (success_msg)
