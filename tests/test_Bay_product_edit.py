
import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result  
from helpers.product_utils import verify_product_update
from helpers.product_utils import update_product_flag

PRODUCT_FILE_PATH = Path("product_name.json")

def test_edit_bulk_products(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        # 1. 등록테스트 제품 검색
        page.goto(URLS["bay_prdList"])
        page.fill("data-testid=input_search", "등록테스트")
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        if row_count < 2:
            print("✅ 검색 결과가 2개 미만이므로 테스트를 스킵합니다.")
            pytest.skip("검색 결과가 2개 이상 존재하지 않아 테스트를 스킵합니다.")
        # 2. 2~3개 제품 랜덤 선택
        indices = random.sample(range(row_count), k=2)
        selected_names = []

        for idx in indices:
            row = rows.nth(idx)
            row.locator("td:nth-child(1)").click()
            name = row.locator("td:nth-child(5)").inner_text().strip()
            selected_names.append(name)

        # 3. 일괄 수정 진입
        page.click("data-testid=btn_edit_bulk")
        page.wait_for_timeout(2000)

                # 2. 2개 제품만 수정하도록 설정
        product_sections = page.locator("div[data-orientation='vertical']")
        updated_names = []

        # 2개 제품만 수정하도록 for loop 변경
        for i in range(min(2, product_sections.count())):  # 최대 2개만 수정
            section = product_sections.nth(i)

            # 4.1. 제품명 수정
            origin_name = section.locator("[data-testid=input_prdname_kor]").input_value()
            new_name = origin_name + "_수정됨"
            section.locator("[data-testid=input_prdname_kor]").fill(new_name)

            # 제품명 리스트에 새 이름 추가
            updated_names.append(new_name)

        # 업데이트된 제품명 출력
        print(f"업데이트된 제품명들: {updated_names}")



        # 5. 저장
        # page.click("data-testid=btn_save")
        page.locator("button:has-text('완료')").click()
        page.wait_for_timeout(1000)

        # 6. 제품관리 에서 수정값 검증
        verify_product_update(page, updated_names)

        update_product_flag(new_name, stock=10, order_flag=1, delivery_status=1)

        # Test result
        msg = f"[PASS][제품관리] 일괄 제품 수정 완료: {updated_names}"
        save_test_result("test_edit_bulk_products", msg, status="PASS")
    
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 일괄 제품 수정 실패\n에러 내용: {str(e)}"
        save_test_result("test_edit_bulk_products", fail_msg, status="FAIL")
        raise
