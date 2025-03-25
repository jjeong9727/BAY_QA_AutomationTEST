import pytest
import requests
import random
from playwright.sync_api import sync_playwright
from config import URLS, Account

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

# 🔔테스트 아이디 부여 필요🔔
def test_add_categories(browser):
    page = browser.new_page()
    page.goto(URLS["login"])

    # 로그인
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    # 제품 등록 페이지로 이동
    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    # 테스트용 구분/종류/제조사 이름 생성
    name_type = f"구분{random.randint(1000, 9999)}"
    name_ctg = f"종류{random.randint(1000, 9999)}"
    name_maker = f"제조사{random.randint(1000, 9999)}"

    #구분 추가
    page.click("data-testid=btn_typeadd")
    empty_type_inputs = page.locator("data-testid=input_type").all()
    for input_box in empty_type_inputs:
        if input_box.input_value().strip() == "":
            input_box.fill(name_type)
            break

    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)
    print(f"구분 추가 완료: {name_type}")

    #종류 추가
    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)
    page.click("data-testid=btn_ctgadd")
    empty_ctg_inputs = page.locator("data-testid=input_ctg").all()
    for input_box in empty_ctg_inputs:
        if input_box.input_value().strip() == "":
            input_box.fill(name_ctg)
            break

    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)
    print(f"종류 추가 완료: {name_ctg}")

    #제조사 추가
    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)
    page.click("data-testid=btn_makeradd")
    empty_maker_inputs = page.locator("data-testid=input_maker").all()
    for input_box in empty_maker_inputs:
        if input_box.input_value().strip() == "":
            input_box.fill(name_maker)
            break

    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)
    print(f"제조사 추가 완료: {name_maker}")
