import pytest
from playwright.sync_api import Page
from config import URLS, Account


def register_category(page: Page, tab_testid: str, name_kr: str, name_en: str):
    page.click(f"data-testid={tab_testid}")
    page.wait_for_timeout(300)
    page.click("data-testid=btn_add")
    page.locator("data-testid=input_kor").last.fill(name_kr)
    page.locator("data-testid=input_eng").last.fill(name_en)
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=60000)


def try_duplicate_registration(page: Page, tab_testid: str, name_kr: str, name_en: str):
    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)
    page.click(f"data-testid={tab_testid}")
    page.wait_for_timeout(300)
    page.click("data-testid=btn_add")
    page.locator("data-testid=input_kor").last.fill(name_kr)
    page.locator("data-testid=input_eng").last.fill(name_en)
    page.click("data-testid=btn_save")
    # 중복이면 저장되지 않고 그대로 페이지 유지되어야 함
    assert page.url == URLS["bay_prdAdd"]
    print(f"[{tab_testid}] 국문명 중복 등록 차단 확인: {name_kr}")


def test_duplicate_category_names(browser):
    page = browser.new_page()
    page.goto(URLS["login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdAdd"])
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    name_kr = "중복테스트"
    name_en1 = "DupOne"
    name_en2 = "DupTwo"

    # 구분
    register_category(page, "tab_type", name_kr, name_en1)
    try_duplicate_registration(page, "tab_type", name_kr, name_en2)

    # 종류
    register_category(page, "tab_category", name_kr, name_en1)
    try_duplicate_registration(page, "tab_category", name_kr, name_en2)

    # 제조사
    register_category(page, "tab_maker", name_kr, name_en1)
    try_duplicate_registration(page, "tab_maker", name_kr, name_en2)
