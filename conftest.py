import pytest
import requests
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(message):
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context(browser):
    # ✅ 여기서 viewport 조절
    context = browser.new_context(
        viewport={"width": 1500, "height": 960},  # 원하는 사이즈로 조절
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
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
