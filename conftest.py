import pytest
import requests
import os
import base64
import datetime
from playwright.sync_api import sync_playwright

# 🔹 Slack Webhook URL (설정한 Webhook URL을 여기에 입력)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_message(message):
    """Slack으로 메시지 전송"""
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

@pytest.fixture(scope="function")
def browser():
    """✅ Playwright 브라우저 실행 및 종료"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """✅ Playwright 새 페이지 생성"""
    page = browser.new_page()
    yield page
    page.close()




# # ✅ 스크린샷 저장 폴더 설정
# screenshot_dir = "C:/Users/kjeon/OneDrive/Desktop/QA/자동화/Test_Report/Screenshots"

# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """테스트 실패 시 스크린샷을 저장하고 HTML 리포트에 포함"""
#     outcome = yield
#     result = outcome.get_result()

#     if call.when == "call" and result.failed:  # 테스트 실패 시 실행
#         page = item.funcargs.get("page", None)
#         if page:
#             # ✅ 현재 날짜와 시간 설정
#             current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 리포트 파일용
#             current_time = datetime.datetime.now().strftime("%H-%M-%S")  # 스크린샷 파일용

#             # ✅ 스크린샷 파일명
#             screenshot_name = f"{item.name}_{current_date}_{current_time}.png"

#             # ✅ 폴더가 없으면 생성
#             if not os.path.exists(screenshot_dir):
#                 os.makedirs(screenshot_dir)

#             # ✅ 스크린샷 저장 경로
#             screenshot_path = os.path.join(screenshot_dir, screenshot_name)

#             # ✅ 스크린샷 저장
#             page.screenshot(path=screenshot_path)

#             # ✅ Base64 변환 후 리포트에 추가
#             with open(screenshot_path, "rb") as image_file:
#                 encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
#                 pytest_html = item.config.pluginmanager.getplugin("html")
#                 extra = getattr(item.config, "_html", None)
#                 if extra:
#                     extra.append(pytest_html.extras.image(f"data:image/png;base64,{encoded_string}"))

#             print(f"📸 스크린샷 저장됨: {screenshot_path}")  # 로그 출력
