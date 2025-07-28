import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.product_utils import verify_product_update
from helpers.product_utils import update_product_flag
from helpers.common_utils import bay_login

PRODUCT_FILE_PATH = Path("product_name.json")

# JSON에서 조건에 맞는 제품을 찾는 함수
def get_deletable_products():
    with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    # order_flag가 0이고 stock_qty가 0인 제품 찾기
    deletable_products = [p for p in products if p.get("order_flag") == 0 and p.get("stock_qty", 0) == 0]
    
    return deletable_products

def test_edit_products(page):
    try:
        bay_login(page)

        # 1. JSON에서 조건에 맞는 제품 하나 가져오기
        product = get_deletable_products()[0]  # 또는 get_editable_product()
        product_name = product["kor"]
        print(f"🎯 수정 대상 제품명: {product_name}")

        # 2. 제품 검색
        page.goto(URLS["bay_prdList"])
        page.wait_for_timeout(2000)
        page.fill('[data-testid="input_search"]', product_name)
        page.wait_for_timeout(1000)
        page.click('[data-testid="btn_search"]')
        page.wait_for_timeout(2000)

        # 3. 검색 결과에서 해당 행의 수정 버튼 클릭
        rows = page.locator("table tbody tr")
        row_count = rows.count()

        for i in range(row_count):
            edit_button = rows.nth(i).locator("td:nth-child(11) >> text=수정")
            if edit_button.is_visible():
                print(f"✅ {i}번째 행의 수정 버튼 클릭")
                edit_button.click()
                break

        # 4. 제품명, 제조사 수정
        page.wait_for_timeout(2000)
        input_kor = page.locator('input[data-testid="input_prdname_kor"]')
        origin_name = input_kor.input_value()
        new_name = f"[수정]{origin_name}"
        input_kor.fill(new_name)
        print(f"✏️ 제품명 수정: {origin_name} → {new_name}")

        # 제조사 수정
        new_maker = "중복테스트"
        page.locator('[data-testid="drop_maker_trigger"]').click()
        page.wait_for_timeout(1000)
        page.fill('[data-testid="drop_maker_search"]', new_maker)
        page.wait_for_timeout(1000)
        page.locator('[data-testid="drop_maker_item"]', has_text=new_maker).click()
        page.wait_for_timeout(1000)
        print(f"🏷️ 제조사 수정 → {new_maker}")

        # 자동 발주 수량 0 입력 시 토스트 확인
        page.locator("data-testid=input_stk_qty").last.fill("0")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_save").click()
        expect(page.locator("data-testid=toast_order_min")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_stk_qty").last.fill("5")
        page.wait_for_timeout(1000)

        # 저장
        txt_edit = "제품을 수정하시겠습니까?"
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_save").click()
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_edit")).to_have_text(txt_edit, timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        # 6. 제품관리에서 수정값 검증 (검증 후 PASS인 경우에만 업데이트)
        print("✅ 수정값 검증 시작")
        if verify_product_update(page, new_name):  # 수정된 이름이 UI에 반영되었는지 검증
            print("✅ 수정된 이름이 UI에 반영됨")
            # UI 검증 후 수정이 반영되었으면 update_product_flag를 활용하여 JSON 업데이트
            update_product_flag(name_kor=origin_name, kor=new_name, maker=new_maker)
            
            msg = f"[PASS][제품관리] 제품 수정 완료: {new_name}"
        else:
            raise Exception("❌ 수정된 제품명이 UI에 반영되지 않았습니다.")
    
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 제품 수정 실패\n에러 내용: {str(e)}"
        raise
