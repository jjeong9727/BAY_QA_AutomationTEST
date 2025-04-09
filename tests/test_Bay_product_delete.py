import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result  

PRODUCT_FILE_PATH = Path("product_name.json")

def get_deletable_products_from_json():
    try:
        with open("product_name.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        deletable = [item["kor"] for item in data if item.get("order_flag") == 0 and item.get("stock", 0) == 0]
        return deletable
    except Exception as e:
        error_message = f"Error while fetching deletable products: {str(e)}"
        save_test_result("get_deletable_products_from_json", error_message, status="ERROR")
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
        save_test_result("remove_product_name_by_kor", error_message, status="ERROR")
        raise

def check_delete(page, product_name: str) -> bool:
    try:
        rows = page.locator("table tbody tr").all()
        for row in rows:
            columns = row.locator("td").all_inner_texts()
            if len(columns) >= 5 and product_name in columns[4]:
                return False
        return True
    except Exception as e:
        error_message = f"Error during delete check for {product_name}: {str(e)}"
        save_test_result("check_delete", error_message, status="ERROR")
        raise

def delete_product_and_verify(page: Page, row_index: int):
    try:
        product_name = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(5)").inner_text().strip()
        product_display_name = product_name.splitlines()[0]

        delete_button = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(9) button").nth(1)
        delete_button.click()

        page.locator("div[role=alertdialog]").get_by_text("삭제", exact=True).click()
        page.wait_for_timeout(2000)
        page.reload()

        if check_delete(page, product_name):
            msg = f"[PASS][제품관리] 제품 삭제 테스트 (삭제된 제품: '{product_display_name}')"
            print(msg)
            remove_product_name_by_kor(product_display_name)  # ✅ JSON에서 제거
            save_test_result("delete_product_and_verify", msg, status="PASS")
        else:
            fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 실패 (리스트에 존재)"
            print(fail_msg)
            save_test_result("delete_product_and_verify", fail_msg, status="FAIL")
            assert False, fail_msg
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 중 예외 발생\n에러: {str(e)}"
        save_test_result("delete_product_and_verify", fail_msg, status="FAIL")
        print(fail_msg)
        raise

def test_delete_product(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])

        deletable_names = get_deletable_products_from_json()
        if not deletable_names:
            msg = "❌ 삭제 가능한 제품이 없습니다."
            save_test_result("test_delete_product", msg, status="FAIL")
            print(msg)
            return

        target_name = random.choice(deletable_names)

        page.goto(URLS["bay_prdList"])
        page.fill("input[placeholder='제품명 검색']", target_name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            msg = f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다."
            save_test_result("test_delete_product", msg, status="FAIL")
            print(msg)
            return

        delete_product_and_verify(page, row_index=0)
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 제품 삭제 중 예외 발생\n에러 내용: {str(e)}"
        save_test_result("test_delete_product", fail_msg, status="FAIL")
        print(fail_msg)
        raise

def test_bulk_delete_products(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])

        deletable_names = get_deletable_products_from_json()
        if not deletable_names:
            msg = "❌ 일괄 삭제 가능한 제품이 없습니다."
            save_test_result("test_bulk_delete_products", msg, status="FAIL")
            print(msg)
            return

        selected_names = random.sample(deletable_names, min(len(deletable_names), random.randint(1, 3)))

        page.goto(URLS["bay_prdList"])
        selected_product_names = []

        for name in selected_names:
            page.fill("input[placeholder='제품명 검색']", name)
            page.click("data-testid=btn_search")
            page.wait_for_timeout(500)

            row = page.locator("table tbody tr").nth(0)
            if row.is_visible():
                row.locator("td:nth-child(1)").click()
                selected_product_names.append(name)

        if not selected_product_names:
            msg = "✅ 조건에 맞는 제품이 없어서 삭제를 스킵합니다."
            save_test_result("test_bulk_delete_products", msg, status="PASS")
            print(msg)
            return

        page.get_by_text("일괄 삭제", exact=True).click()
        alert_popup = page.locator("div[role=alertdialog]")  
        alert_popup.get_by_text("삭제", exact=True).click()
        page.wait_for_timeout(2000)
        page.reload()

        failed = [name for name in selected_product_names if not check_delete(page, name)]

        if not failed:
            msg = f"[PASS][제품관리] 제품 {len(selected_product_names)}개 일괄 삭제 성공: {selected_product_names}"
            save_test_result("test_bulk_delete_products", msg, status="PASS")
            print(msg)
        else:
            fail_msg = f"[FAIL][제품관리] 일부 제품 삭제 실패: {failed}"
            save_test_result("test_bulk_delete_products", fail_msg, status="FAIL")
            assert False, fail_msg
    except Exception as e:
        fail_msg = f"[FAIL][제품관리] 일괄 삭제 중 예외 발생\n에러 내용: {str(e)}"
        save_test_result("test_bulk_delete_products", fail_msg, status="FAIL")
        print(fail_msg)
        raise
