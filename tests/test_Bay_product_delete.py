import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import remove_products_from_json
from helpers.common_utils import bay_login

PRODUCT_FILE_PATH = Path("product_name.json")

def get_deletable_products_from_json():
    try:
        with open("product_name.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        deletable = [item["kor"] for item in data if item.get("supplier") == "자동화업체, 권정의" and item.get("stock_qty", 0) == 0]
        return deletable
    except Exception as e:
        error_message = f"Error while fetching deletable products: {str(e)}"
        
        raise

def remove_product_name_by_kor(kor_name: str):
    try:
        if not PRODUCT_FILE_PATH.exists():
            return
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        updated = [item for item in data if item["kor"] != kor_name]
        with open(PRODUCT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
    except Exception as e:
        error_message = f"Error while removing product {kor_name} from json: {str(e)}"
        
        raise

def check_delete(page, product_name: str) -> bool:
    try:
        rows = page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            if len(columns) >= 5 and product_name in columns[3]:
                return False
        return True
    except Exception as e:
        error_message = f"Error during delete check for {product_name}: {str(e)}"
        
        raise

def delete_product_and_verify(page: Page, row_index: int):
    try:
        product_name = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(4)").inner_text().strip()
        product_display_name = product_name.splitlines()[0]

        delete_button = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(12) button").nth(1)  # 0부터 시작하므로 1은 두 번째 버튼
        delete_button.click()


        page.click("data-testid=btn_del")
        page.wait_for_timeout(500)
        page.reload()
        page.wait_for_timeout(1000)

        if check_delete(page, product_name):
            msg = f"[PASS][제품관리] 제품 삭제 테스트 (삭제된 제품: '{product_display_name}')"
            print(msg)
            remove_product_name_by_kor(product_display_name)  # ✅ JSON에서 제거
        else:
            fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 실패 (리스트에 존재)"
            print(fail_msg)
            
            assert False, fail_msg
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 중 예외 발생\n에러: {str(e)}"
        
        print(fail_msg)
        raise

def test_delete_product(page):
    try:
        bay_login(page)

        deletable_names = get_deletable_products_from_json()
        if not deletable_names:
            msg = "❌ 삭제 가능한 제품이 없습니다."
            print(msg)
            return

        target_name = random.choice(deletable_names)

        page.goto(URLS["bay_prdList"])
        page.fill("data-testid=input_search", target_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            msg = f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다."
            print(msg)
            return

        delete_product_and_verify(page, row_index=0)

        remove_products_from_json(target_name)


    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 제품 삭제 중 예외 발생\n에러 내용: {str(e)}"
        print(fail_msg)
        raise

def test_bulk_delete_products(page):
    try:
        # 로그인
        bay_login(page)


        # 일괄 삭제 가능한 제품 검색
        deletable_names = get_deletable_products_from_json()
        if not deletable_names:
            msg = "❌ 일괄 삭제 가능한 제품이 없습니다."
            print(msg)
            return
        # 2개 이상이면 2개, 1개면 1개, 0개면 빈 리스트
        selected_names = random.sample(deletable_names, min(len(deletable_names), 2))

        # 제품 리스트 페이지로 이동
        
        selected_product_names = []

        for name in selected_names:
            page.fill("data-testid=input_search", name)
            page.wait_for_timeout(1000)
            page.click("data-testid=btn_search")
            page.wait_for_timeout(1000)

            row = page.locator("table tbody tr").nth(0)
            if row.is_visible():
                row.locator("td:nth-child(1)").click()
                selected_product_names.append(name)

        if not selected_product_names:
            msg = "✅ 조건에 맞는 제품이 없어서 삭제를 스킵합니다."
            print(msg)
            return

        # 일괄 삭제 버튼 클릭
        page.click("data-testid=btn_del_bulk")
        page.wait_for_timeout(2000)
        page.locator("data-testid=btn_del").click()
        page.wait_for_timeout(2000)

        # 삭제 후, 제품이 목록에서 사라졌는지 확인
        failed = []
        for name in selected_product_names:
            if not check_delete(page, name):  # 삭제 확인 함수 호출
                failed.append(name)

        if failed:
            fail_msg = f"[FAIL][제품관리] 일부 제품 삭제 실패: {failed}"
            print(fail_msg)
            assert False, fail_msg
        else:
            msg = f"[PASS][제품관리] 제품 {len(selected_product_names)}개 일괄 삭제 성공: {selected_product_names}"
            print(msg)

            remove_products_from_json(selected_product_names)

    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 일괄 삭제 중 예외 발생\n에러 내용: {str(e)}"
        print(fail_msg)
        raise

