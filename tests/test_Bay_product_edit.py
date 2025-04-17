import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import verify_product_update
from helpers.product_utils import update_product_flag

PRODUCT_FILE_PATH = Path("product_name.json")

# JSON에서 조건에 맞는 제품을 찾는 함수
def get_deletable_products():
    with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    # order_flag가 0이고 stock_qty가 0인 제품 찾기
    deletable_products = [p for p in products if p.get("order_flag") == 0 and p.get("stock_qty", 0) == 0]
    
    return deletable_products

def test_edit_bulk_products(browser):
    try:
        print("✅ 브라우저 새 페이지 생성")
        page = browser.new_page()
        print("✅ 로그인 페이지로 이동")
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        # 1. 조건에 맞는 제품을 JSON에서 찾아 수정 대상으로 삼음
        products_to_edit = get_deletable_products()
        print(f"✅ 찾은 삭제 대상 제품 수: {len(products_to_edit)}")

        if not products_to_edit:
            print("✅ 수정 대상 제품이 없습니다.")
            pytest.skip("수정 대상 제품이 없습니다.")

        # 2. 등록테스트 제품 검색
        print("✅ 등록테스트 제품 검색")
        page.goto(URLS["bay_prdList"])
        page.fill("data-testid=input_search", "등록테스트")
        page.wait_for_timeout(500)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        print(f"✅ 검색된 제품 수: {row_count}")
        if row_count < 2:
            print("✅ 검색 결과가 2개 미만이므로 테스트를 스킵합니다.")
            pytest.skip("검색 결과가 2개 이상 존재하지 않아 테스트를 스킵합니다.")
        
        # 2~3개 제품 랜덤 선택
        print("✅ 제품을 랜덤으로 선택")
        indices = random.sample(range(row_count), k=2)
        selected_names = []

        for idx in indices:
            row = rows.nth(idx)
            row.locator("td:nth-child(1)").click()
            name = row.locator("td:nth-child(5)").inner_text().strip()
            selected_names.append(name)

        # 3. 일괄 수정 진행
        page.click("data-testid=btn_edit_bulk")
        page.wait_for_timeout(2000)

        # 4. 페이지 내 모든 제품명 입력 필드를 찾고, 첫 번째와 두 번째 제품을 수정
        input_kor_elements = page.locator("input[data-testid='input_prdname_kor']")
        print(f"✅ 수정 대상 제품명 필드 수: {input_kor_elements.count()}")

        updated_names = []
        
        # 첫 번째 제품 수정
        print("✅ 첫 번째 제품 수정 시작")
        first_input = input_kor_elements.nth(0)
        origin_name_first = first_input.input_value()
        new_name_first = origin_name_first + "."
        first_input.fill(new_name_first)
        updated_names.append(new_name_first)
        print(origin_name_first)
        print(new_name_first)

        # 두 번째 제품 수정
        print("✅ 두 번째 제품 수정 시작")
        second_input = input_kor_elements.nth(1)
        origin_name_second = second_input.input_value()
        new_name_second = origin_name_second + "."
        second_input.fill(new_name_second)
        updated_names.append(new_name_second)
        print(new_name_second)

        # 저장
        print("✅ 수정 완료 후 저장 클릭")
        page.locator("button:has-text('완료')").click()
        page.wait_for_timeout(1000)
        confirm_btn = page.locator("data-testid=btn_confirm")
        if confirm_btn.is_visible():
            confirm_btn.click()
            page.wait_for_timeout(500)

        # 6. 제품관리에서 수정값 검증 (검증 후 PASS인 경우에만 업데이트)
        print("✅ 수정값 검증 시작")
        if verify_product_update(page, updated_names):  # 수정된 이름이 UI에 반영되었는지 검증
            print("✅ 수정된 이름이 UI에 반영됨")
            # UI 검증 후 수정이 반영되었으면 update_product_flag를 활용하여 JSON 업데이트
            for name in updated_names:
                # update_product_flag를 이용해 수정된 제품의 속성 업데이트
                update_product_flag(name)
            
            msg = f"[PASS][제품관리] 일괄 제품 수정 완료: {updated_names}"
        else:
            raise Exception("❌ 수정된 제품명이 UI에 반영되지 않았습니다.")
    
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 일괄 제품 수정 실패\n에러 내용: {str(e)}"
        raise
