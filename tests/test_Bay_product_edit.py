import pytest
import requests
import random
from playwright.sync_api import sync_playwright
from config import URLS, Account


def test_edit_single_product(browser):
    from helpers.verify_product_update import verify_product_update

    from helpers.product_utils import update_product_flag

    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    base_url = URLS["bay_prdList"]
    product_found = False
    current_page = 1

    # 1. 페이지를 순회하며 "등록테스트" 제품을 찾기
    while not product_found:
        page.goto(f"{base_url}?page={current_page}")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            name_cell = rows.nth(i).locator("td:nth-child(5)")
            name_text = name_cell.inner_text().strip()

            if name_text.startswith("등록테스트"):
                edit_btn = rows.nth(i).locator("button:has-text('수정')")
                edit_btn.click()
                product_found = True
                target_name = name_text
                break

        if not product_found:
            if rows.count() == 0:
                break
            current_page += 1

    assert product_found, "❌ 수정할 등록테스트 제품을 찾을 수 없습니다."

    # 2. 수정 화면에서 값 변경
    page.wait_for_timeout(1000)

    page.click("data-testid=drop_type_trigger")
    page.wait_for_timeout(500)
    type_options = page.locator("data-testid=drop_type_item").all_inner_texts()
    current_type = page.locator("data-testid=drop_type_trigger").inner_text().strip()

    new_type = None
    for opt in type_options:
        if opt != current_type:
            new_type = opt
            break

    assert new_type, "❌ 다른 구분값을 찾을 수 없습니다."
    page.locator("data-testid=drop_type_item", has_text=new_type).click()

    new_name = target_name + "_수정됨"
    page.fill("data-testid=input_prdname_kor", new_name)

    page.click("data-testid=btn-save")
    page.wait_for_url(URLS["bay_prdList"], timeout=10000)
    page.wait_for_timeout(1000)

    update_product_flag(new_name, undeletable=True)

    verify_product_update(page, [new_name])




def test_edit_bulk_products(browser):
    from helpers.verify_product_update import verify_product_update

    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    # 1. 등록테스트 제품 검색
    page.goto(URLS["bay_prdList"])
    page.fill("input[placeholder='제품명 검색']", "등록테스트")
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()
    assert row_count >= 2, "❌ 검색 결과가 2개 이상 존재하지 않습니다."

    # 2. 2~3개 제품 랜덤 선택
    indices = random.sample(range(row_count), k=random.randint(2, min(3, row_count)))
    selected_names = []

    for idx in indices:
        row = rows.nth(idx)
        checkbox = row.locator("td:nth-child(1) input[type=checkbox]")
        checkbox.click()
        name = row.locator("td:nth-child(5)").inner_text().strip()
        selected_names.append(name)

    # 3. 일괄 수정 진입
    page.click("data-testid=btn_edit_bulk")
    page.wait_for_timeout(2000)

    # 4. 제품별 개별 수정
    product_sections = page.locator("div[class*='product-edit-box']")
    updated_names = []

    for i in range(product_sections.count()):
        section = product_sections.nth(i)

        origin_name = section.locator("[data-testid=input_prdname_kor]").input_value()
        new_name = origin_name + "_수정됨"

        section.locator("[data-testid=drop_type_trigger]").click()
        page.wait_for_timeout(300)
        options = page.locator("[data-testid=drop_type_item]").all_inner_texts()
        current = section.locator("[data-testid=drop_type_trigger]").inner_text()
        for opt in options:
            if opt != current:
                page.locator("[data-testid=drop_type_item]", has_text=opt).click()
                break

        section.locator("[data-testid=input_prdname_kor]").fill(new_name)
        updated_names.append(new_name)

    # 5. 저장
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=10000)
    page.wait_for_timeout(1000)

    # 6. 제품관리 & 재고관리에서 수정값 검증
    verify_product_update(page, updated_names)
