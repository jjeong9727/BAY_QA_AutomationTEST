import random
from datetime import datetime
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

# # 개별삭제
# def test_delete_product(browser):
#     page = browser.new_page()
#     page.goto(URLS["bay_login"])
#     page.fill("data-testid=input_id", Account["testid"])
#     page.fill("data-testid=input_pw", Account["testpw"])
#     page.click("data-testid=btn_login")
#     page.wait_for_url(URLS["bay_home"])

#     # 서버와 JSON 파일 싱크 맞추기
#     valid_product_names = sync_product_names_with_server(page)

#     if not valid_product_names:
#         print("❌ 유효한 제품이 없습니다.")
#         return

#     # 삭제 가능한 제품 목록 확인
#     deletable_names = get_deletable_products_from_json()
#     if not deletable_names:
#         print("❌ 삭제 가능한 제품이 없습니다.")
#         return

#     target_name = random.choice(deletable_names)

#     # 제품 목록 페이지로 이동
#     page.goto(URLS["bay_prdList"])

#     # 존재 여부 확인
#     if not is_product_exist(page, target_name):
#         print(f"❌ 제품 '{target_name}'이(가) 제품 리스트에 존재하지 않아 삭제 불가")
#         return

#     # 삭제 화면 진입 및 검색
#     page.fill("input[placeholder='제품명 검색']", target_name)
#     page.locator("button:has-text('검색')").click()
#     page.wait_for_timeout(1000)

#     rows = page.locator("table tbody tr")
#     if rows.count() == 0:
#         print(f"❌ 제품 '{target_name}' 을(를) 찾을 수 없습니다.")
#         return

#     # 첫 번째 행의 첫 번째 열 클릭하여 체크박스 선택
#     first_row = rows.nth(0)
#     first_cell = first_row.locator("td").nth(0)
#     first_cell.click()

#     # 삭제 버튼 클릭
#     row = rows.nth(0)
#     target_name = row.locator("td:nth-child(5)").inner_text().strip()
#     row.locator("button:has-text('삭제')").click()

#     # 삭제 확인 대화상자 처리
#     page.wait_for_selector("[role='alertdialog']")
#     page.locator("[role='alertdialog'] button:has-text('삭제')").click()

#     page.wait_for_timeout(1000)

#     # 삭제 확인
#     page.wait_for_timeout(1000)
#     assert not is_product_exist(page, target_name), f"❌ 제품 '{target_name}' 삭제 실패"
#     print(f"✅ 제품 '{target_name}' 삭제 성공")

#     # JSON 파일에서 삭제된 제품 제거
#     remove_products_from_json([target_name])








# def test_bulk_delete_registered_products(browser):
#     page = browser.new_page()
#     page.goto(URLS["bay_login"])
#     page.fill("data-testid=input_id", Account["testid"])
#     page.fill("data-testid=input_pw", Account["testpw"])
#     page.click("data-testid=btn_login")
#     page.wait_for_url(URLS["bay_home"])

#     # 제품 관리 페이지로 이동
#     page.goto(URLS["bay_prdList"])

#     # "등록테스트"로 제품 검색
#     page.fill("input[placeholder='제품명 검색']", "등록테스트")
#     page.locator("button:has-text('검색')").click()
#     page.wait_for_timeout(1000)

#     # JSON에서 제품명 목록 가져오기
#     json_data = get_all_product_names()
#     deletable_products = []
#     rows = page.locator("table tbody tr")
    
#     # JSON 제품명과 비교하여 2개 제품 선택
#     for i in range(rows.count()):
#         row = rows.nth(i)
#         prdname = row.locator("td:nth-child(5)").inner_text().strip()

#         # JSON에서 'kor' 필드로 제품명을 비교
#         match = next((item for item in json_data if item.get("kor") == prdname), None)
#         if match and match.get("stock", 0) == 0 and match.get("order_flag", 0) == 0:
#             # 조건에 맞는 제품 찾으면 체크박스를 클릭하여 선택
#             row.locator("td:nth-child(1)").click()  # 체크박스를 클릭한 1열
#             deletable_products.append(prdname)

#         # 삭제 대상이 2개 이상이면 루프 탈출
#         if len(deletable_products) >= 2:
#             break

#     if len(deletable_products) < 2:
#         print(f"❌ 삭제 가능한 제품이 2개 미만입니다. 현재 삭제 대상: {deletable_products}")
#         return

#     # 첫 번째 삭제 버튼 클릭 (일괄 삭제)
#     page.locator("button:has-text('삭제')").click()

#     # 삭제 확인 대화상자 처리
#     page.wait_for_selector("[role='alertdialog']")
#     page.locator("[role='alertdialog'] button:has-text('삭제')").click()

#     page.wait_for_timeout(1000)  # 잠시 대기

#     # 삭제한 제품들 확인
#     for product_name in deletable_products:
#         assert not is_product_exist(page, product_name), f"❌ 제품 '{product_name}' 삭제 실패"
#         print(f"✅ 제품 '{product_name}' 삭제 성공")

#     # JSON 파일에서 삭제된 제품 제거
#     remove_products_from_json(deletable_products)

#     print(f"[PASS] {len(deletable_products)}개 제품 일괄 삭제 완료")

#     # 삭제한 제품들이 리스트에서 없는지 확인
#     for product_name in deletable_products:
#         page.goto(URLS["bay_prdList"])  # 제품 리스트 페이지로 이동
#         page.fill("input[placeholder='제품명 검색']", product_name)
#         page.locator("button:has-text('검색')").click()
#         page.wait_for_timeout(1000)

#         rows = page.locator("table tbody tr")
#         if rows.count() == 0:
#             print(f"[PASS] 제품 '{product_name}' 삭제 완료 확인")
#         else:
#             print(f"❌ 제품 '{product_name}' 삭제 실패")



def test_bulk_delete_registered_products(browser):
    page = browser.new_page()
    print("[LOG] 브라우저 새 페이지 열기")

    page.goto(URLS["bay_login"])
    print("[LOG] 로그인 페이지로 이동")

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    print("[LOG] 로그인 버튼 클릭")
    page.wait_for_url(URLS["bay_home"])
    print("[LOG] 로그인 완료 후 홈 페이지로 이동")

    # 제품 관리 페이지로 이동
    page.goto(URLS["bay_prdList"])
    print("[LOG] 제품 관리 페이지로 이동")

    # "등록테스트_오늘날짜"로 제품 검색
    today_date = datetime.now().strftime("%Y-%m-%d")
    search_term = f"등록테스트_{today_date}"

    page.fill("input[placeholder='제품명 검색']", search_term)
    page.locator("button:has-text('검색')").click()
    print(f"[LOG] '{search_term}' 제품 검색 클릭")
    page.wait_for_timeout(1000)
    print("[LOG] 제품 검색 결과 대기")

    rows = page.locator("table tbody tr")
    print("[LOG] 제품 리스트 로드 완료")

    deletable_products = []

    # 검색된 제품 중에서 조건에 맞는 제품 2개 랜덤 선택
    for i in range(rows.count()):
        row = rows.nth(i)
        prdname = row.locator("td:nth-child(5)").inner_text().strip().splitlines()[0]  # 첫 번째 줄만 가져오기
        print(f"[LOG] 제품명: {prdname} 확인 중")

        # 조건에 맞는 제품 찾으면 삭제 대상에 추가
        deletable_products.append(prdname)
        print(f"[LOG] 삭제 대상 제품 '{prdname}' 추가")

    if len(deletable_products) < 2:
        print(f"❌ 삭제 가능한 제품이 2개 미만입니다. 현재 삭제 대상: {deletable_products}")
        return

    # 랜덤으로 2개의 제품 선택
    selected_products = random.sample(deletable_products, 2)
    print(f"[LOG] 랜덤 선택된 제품: {selected_products}")

    # 선택된 제품 체크박스를 클릭
    rows = page.locator("table tbody tr")  # 검색된 제품 리스트 다시 가져오기
    for prdname in selected_products:
        for i in range(rows.count()):
            row = rows.nth(i)
            row_name = row.locator("td:nth-child(5)").inner_text().strip().splitlines()[0]  # 첫 번째 줄만 가져오기
            if row_name == prdname:
                row.locator("td:nth-child(1)").click()  # 체크박스 클릭
                print(f"[LOG] 제품 '{prdname}' 체크박스 선택 완료")
                break

    # 첫 번째 삭제 버튼 클릭 (일괄 삭제)
    page.locator("button:has-text('삭제')").first.click()
    print("[LOG] 일괄 삭제 버튼 클릭")

    # 삭제 확인 대화상자 처리
    page.wait_for_selector("[role='alertdialog']")
    print("[LOG] 삭제 확인 대화상자 대기")
    page.locator("[role='alertdialog'] button:has-text('삭제')").click()

    page.wait_for_timeout(1000)  # 잠시 대기
    print("[LOG] 삭제 확인 완료 후 대기")

    # 삭제한 제품들 확인
    for product_name in selected_products:
        page.reload()
        page.wait_for_timeout(2000)  # 페이지 로딩 대기
        assert not is_product_exist(page, product_name), f"❌ 제품 '{product_name}' 삭제 실패"
        print(f"✅ 제품 '{product_name}' 삭제 성공")

    print(f"[PASS] {len(selected_products)}개 제품 일괄 삭제 완료")

