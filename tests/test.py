import pytest
import requests
import random
from playwright.sync_api import sync_playwright
from config import URLS, Account


def test_edit_single_product(browser):
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
                # 수정 버튼 클릭
                edit_btn = rows.nth(i).locator("button:has-text('수정')")
                edit_btn.click()
                product_found = True
                target_name = name_text
                target_page = current_page
                break

        if not product_found:
            if rows.count() == 0:
                break  # 더 이상 페이지 없음
            current_page += 1

    assert product_found, "❌ 수정할 등록테스트 제품을 찾을 수 없습니다."

    # 2. 수정 화면에서 값 변경
    page.wait_for_timeout(1000)

    # 기존 구분값 가져오기
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

    # 제품명 수정
    new_name = target_name + "_수정됨"
    page.fill("data-testid=input_prdname_kor", new_name)

    # 저장
    page.click("data-testid=btn-save")
    page.wait_for_url(URLS["bay_prdList"], timeout=10000)
    page.wait_for_timeout(1000)

    # 3. 제품 리스트 페이지에서 변경된 값 확인 (해당 페이지로 이동)
    page.goto(f"{base_url}?page={target_page}")
    page.wait_for_timeout(1000)
    assert page.locator(f"text={new_name}").is_visible(), f"❌ 제품명 수정 미확인: {new_name}"

    # 4. 재고관리 페이지에서 제품명 확인
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    assert page.locator("table tbody td:nth-child(5)", has_text=new_name).is_visible(), f"❌ 재고 목록에 수정된 제품명 없음: {new_name}"

    print(f"[PASS][제품관리] 제품명/구분 수정 확인됨: {new_name}")



def test_edit_bulk_products(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    # 1. 제품 검색 (등록테스트)
    page.goto(URLS["bay_prdList"])
    page.fill("input[placeholder='제품명 검색']", "등록테스트")
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    assert row_count >= 2, "❌ 검색 결과가 2개 이상 존재하지 않습니다."

    # 2. 2개 이상 랜덤 선택
    indices = random.sample(range(row_count), k=random.randint(2, min(3, row_count)))
    selected_names = []
    page_index_map = {}

    for idx in indices:
        row = rows.nth(idx)
        checkbox = row.locator("td:nth-child(1) input[type=checkbox]")
        checkbox.click()
        name = row.locator("td:nth-child(5)").inner_text().strip()
        selected_names.append(name)
        page_index_map[name] = 1  # 검색이므로 모두 첫 페이지로 가정

    # 3. 일괄 수정 버튼 클릭
    page.click("data-testid=btn_edit_bulk")
    page.wait_for_timeout(2000)

    # 4. 수정 화면에서 각 제품의 구분/제품명 수정 (폼 구조)
    product_sections = page.locator("div[class*='product-edit-box']")  # 각 제품별 개별 섹션
    updated_names = []

    for i in range(product_sections.count()):
        section = product_sections.nth(i)

        # 기존 제품명
        origin_name = section.locator("[data-testid=input_prdname_kor]").input_value()
        new_name = origin_name + "_수정됨"

        # 구분 변경
        section.locator("[data-testid=drop_type_trigger]").click()
        page.wait_for_timeout(300)
        options = page.locator("[data-testid=drop_type_item]").all_inner_texts()
        current = section.locator("[data-testid=drop_type_trigger]").inner_text()
        for opt in options:
            if opt != current:
                page.locator("[data-testid=drop_type_item]", has_text=opt).click()
                break

        # 제품명 수정
        section.locator("[data-testid=input_prdname_kor]").fill(new_name)
        updated_names.append(new_name)

    # 저장
    page.click("data-testid=btn_save")
    page.wait_for_url(URLS["bay_prdList"], timeout=10000)
    page.wait_for_timeout(1000)

    # 5. 제품 관리 페이지에서 수정된 제품명 확인
    for name in updated_names:
        page.goto(f"{URLS['bay_prdList']}?page=1")
        page.wait_for_timeout(1000)
        assert page.locator(f"text={name}").is_visible(), f"❌ 제품 관리 페이지에서 수정 확인 실패: {name}"

    # 6. 재고 관리 페이지에서 제품명 확인
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    for name in updated_names:
        assert page.locator("table tbody td:nth-child(5)", has_text=name).is_visible(), f"❌ 재고 목록에 수정된 제품명 없음: {name}"

    print(f"[PASS][제품관리] {len(updated_names)}개 제품 일괄 수정 확인 완료")