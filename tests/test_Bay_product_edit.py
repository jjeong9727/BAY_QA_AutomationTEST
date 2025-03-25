import pytest
import requests
import random
from playwright.sync_api import sync_playwright
from config import URLS, Account

def select_random_products(page, min_count=1, max_count=3):
    rows = page.locator("table tbody tr").all()
    candidates = []

    for i, row in enumerate(rows):
        columns = row.locator("td").all_inner_texts()
        if len(columns) >= 5 and "등록테스트" in columns[4]:
            candidates.append((i, columns[4]))

    if not candidates:
        print("수정 대상 제품이 없습니다.")
        return []

    count = random.randint(min_count, min(max_count, len(candidates)))
    selected = random.sample(candidates, k=count)

    # 각 제품의 1열 클릭으로 선택 처리
    for idx, _ in selected:
        cell = page.locator(f"table tbody tr >> nth={idx} >> td:nth-child(1)")
        cell.click()

    return selected


@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


def test_bulk_edit_products(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)

    selected = select_random_products(page)
    if not selected:
        return

    page.get_by_text("일괄 수정", exact=True).click()
    page.wait_for_timeout(1000)

    try:
        for row_index, original in selected:
            kor_input = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(5) input").nth(0)
            eng_input = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(5) input").nth(1)

            old_kor = kor_input.input_value()
            old_eng = eng_input.input_value()

            kor_input.fill(old_kor + "_수정됨")
            eng_input.fill(old_eng + "_MOD")

        page.get_by_text("일괄 저장", exact=True).click()
        page.wait_for_url(URLS["bay_prdList"])
        page.wait_for_timeout(2000)

        all_passed = True
        for _, original in selected:
            edited_kor = original.splitlines()[0] + "_수정됨"
            if not page.locator(f"text={edited_kor}").is_visible():
                all_passed = False
                print(f"❌ 수정 실패: {edited_kor}")

        if all_passed:
            msg = f"[PASS][제품관리] {len(selected)}개 제품 일괄 수정 테스트"
            print(msg)

    except Exception as e:
        error_msg = f"[FAIL][제품관리] 일괄 수정 중 예외 발생\n에러 내용: {str(e)}"
        print(error_msg)
        raise
