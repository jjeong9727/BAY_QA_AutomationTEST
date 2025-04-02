import pytest
import random
import json
from pathlib import Path
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import is_product_exist, get_all_product_names, remove_products_from_json, sync_product_names_with_server

PRODUCT_FILE_PATH = Path("product_name.json")

def get_deletable_products_from_json():
    with open("product_name.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    deletable = [item["kor"] for item in data if item.get("order_flag") == 0 and item.get("stock", 0) == 0]
    return deletable

def remove_product_name_by_kor(kor_name: str):
    if not PRODUCT_FILE_PATH.exists():
        return
    with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    updated = [item for item in data if item["kor"] != kor_name]
    with open(PRODUCT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

def check_delete(page, product_name: str) -> bool:
    rows = page.locator("table tbody tr").all()
    for row in rows:
        columns = row.locator("td").all_inner_texts()
        if len(columns) >= 5 and product_name in columns[4]:
            return False
    return True

def delete_product_and_verify(page: Page, row_index: int):
    product_name = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(5)").inner_text().strip()
    product_display_name = product_name.splitlines()[0]

    try:
        delete_button = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(9) button").nth(1)
        delete_button.click()

        page.locator("div[role=alertdialog]").get_by_text("삭제", exact=True).click()
        page.wait_for_timeout(2000)
        page.reload()

        if check_delete(page, product_name):
            msg = f"[PASS][제품관리] 제품 삭제 테스트 (삭제된 제품: '{product_display_name}')"
            print(msg)
            remove_product_name_by_kor(product_display_name)  # ✅ JSON에서 제거
        else:
            fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 실패 (리스트에 존재)"
            print(fail_msg)
            assert False, fail_msg

    except Exception as e:
        raise Exception(f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 중 예외 발생\n에러: {str(e)}")

# 개별삭제
def test_delete_product(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    # 서버와 JSON 파일 싱크 맞추기
    valid_product_names = sync_product_names_with_server(page)

    if not valid_product_names:
        print("❌ 유효한 제품이 없습니다.")
        return

    # 삭제 가능한 제품 목록 확인
    deletable_names = get_deletable_products_from_json()
    if not deletable_names:
        print("❌ 삭제 가능한 제품이 없습니다.")
        return

    target_name = random.choice(deletable_names)

    # 제품 목록 페이지로 이동
    page.goto(URLS["bay_prdList"])

    # 존재 여부 확인
    if not is_product_exist(page, target_name):
        print(f"❌ 제품 '{target_name}'이(가) 제품 리스트에 존재하지 않아 삭제 불가")
        return

    # 삭제 화면 진입 및 검색
    page.fill("input[placeholder='제품명 검색']", target_name)
    page.locator("button:has-text('검색')").click()
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    if rows.count() == 0:
        print(f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다.")
        return

    # 첫 번째 행의 첫 번째 열 클릭하여 체크박스 선택
    first_row = rows.nth(0)
    first_cell = first_row.locator("td").nth(0)
    first_cell.click()

    # 삭제 버튼 클릭
    row = rows.nth(0)
    target_name = row.locator("td:nth-child(5)").inner_text().strip()
    row.locator("button:has-text('삭제')").click()

    # 삭제 확인 대화상자 처리
    page.wait_for_selector("[role='alertdialog']")
    page.locator("[role='alertdialog'] button:has-text('삭제')").click()

    page.wait_for_timeout(1000)

    # 삭제 확인
    page.wait_for_timeout(1000)
    assert not is_product_exist(page, target_name), f"❌ 제품 '{target_name}' 삭제 실패"
    print(f"✅ 제품 '{target_name}' 삭제 성공")

    # JSON 파일에서 삭제된 제품 제거
    remove_products_from_json([target_name])





def test_bulk_delete_products(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])

    page.goto(URLS["bay_prdList"])
    json_data = get_all_product_names()
    deleted_names = []
    remembered_product = None
    current_page = 1  # 시작 페이지 번호

    # 제품 삭제 대상 찾기
    while True:
        # 페이지 URL로 이동
        page.goto(f"{URLS['bay_prdList']}?page={current_page}")
        page.wait_for_timeout(1000)  # 페이지 로딩 대기

        rows = page.locator("table tbody tr")
        deletable_found_in_page = False

        for i in range(rows.count()):
            row = rows.nth(i)
            prdname = row.locator("td:nth-child(5)").inner_text().strip()

            # JSON에서 'kor' 필드 사용하여 비교
            match = next((item for item in json_data if item.get("kor") == prdname), None)
            if match and match.get("stock", 0) == 0 and match.get("order_flag", 0) == 0:
                # 첫 번째 열 클릭하여 체크박스 선택
                row.locator("td:nth-child(1)").click()  # 체크박스를 포함한 1열 클릭
                deleted_names.append(prdname)
                deletable_found_in_page = True

                # 첫 번째 삭제 가능한 제품을 기억
                if not remembered_product:
                    remembered_product = prdname

        # 삭제 대상이 있다면 일괄 삭제
        if deletable_found_in_page:
            break  # 삭제 대상 확보 → 루프 탈출

        # 페이지를 넘어가야 할 때
        current_page += 1

    if not deleted_names:
        print("❌ 전체 페이지에서 삭제 가능한 제품이 없습니다.")
        return

    # 첫 번째 삭제 버튼 클릭
    first_delete_button = page.locator("button:has-text('삭제')").first()
    first_delete_button.click()

    # 삭제 확인 대화상자 처리
    page.wait_for_selector("[role='alertdialog']")
    page.locator("[role='alertdialog'] button:has-text('삭제')").click()

    page.wait_for_timeout(1000)

    # 삭제 확인
    for name in deleted_names:
        assert not is_product_exist(page, name), f"❌ 제품 '{name}' 삭제 실패"
        print(f"✅ 제품 '{name}' 삭제 성공")

    # JSON 파일에서 삭제된 제품 제거
    remove_products_from_json(deleted_names)

    print(f"[PASS] {len(deleted_names)}개 제품 일괄 삭제 완료")

    # 기억한 제품이 삭제되었는지 확인
    if remembered_product:
        page.goto(URLS["bay_prdList"])  # 제품 리스트 페이지로 이동
        page.fill("input[placeholder='제품명 검색']", remembered_product)
        page.locator("button:has-text('검색')").click()
        page.wait_for_timeout(1000)

        # 제품이 리스트에 없다면 PASS 처리
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            print(f"[PASS] 제품 '{remembered_product}' 삭제 완료 확인")
        else:
            print(f"❌ 제품 '{remembered_product}' 삭제 실패")
