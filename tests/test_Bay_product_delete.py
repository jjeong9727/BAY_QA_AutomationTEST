import pytest
import requests
import random
import os
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account




@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


def check_delete(page, product_name: str) -> bool:
    rows = page.locator("table tbody tr").all()
    for row in rows:
        columns = row.locator("td").all_inner_texts()
        if len(columns) >= 5 and product_name in columns[4]:
            return False  # 제품이 여전히 존재함
    return True  # 제품이 삭제된 상태

# 제품 삭제 후 판단
def delete_product_and_verify(page, row_index: int):
    
    product_name = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(5)").inner_text().strip()

    try:
        # 삭제 버튼 클릭 (9번째 열의 두 번째 버튼)
        delete_button = page.locator(f"table tbody tr >> nth={row_index} >> td:nth-child(9) button").nth(1)
        delete_button.click()

        # Alert 내 삭제 버튼 클릭
        alert_popup = page.locator("div[role=alertdialog]")  
        alert_popup.get_by_text("삭제", exact=True).click()

        page.wait_for_timeout(2000)
        page.reload()

        if check_delete(page, product_name):
            product_display_name = product_name.splitlines()[0]
            msg = f"[PASS][제품관리] 제품 삭제 테스트 (삭제된 제품: '{product_display_name}')"
            print(msg)
        else:
            product_display_name = product_name.splitlines()[0]
            fail_msg = f"[FAIL][제품관리] 제품 '{product_display_name}' 삭제 실패 (리스트에 존재)"
            print(fail_msg)
            assert False, fail_msg

    except Exception as e:
        error_msg = f"[FAIL][제품관리] 제품 '{product_name}' 삭제 중 예외 발생\n에러 내용: {str(e)}"
        print(error_msg)
        raise  # 에러 재발생 시켜서 테스트 실패 처리
# 단일 제품 선택 후 삭제
def test_delete_product(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])
    
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)

    # '등록테스트'가 포함된 제품을 가진 행 인덱스 수집
    rows = page.locator("table tbody tr").all()
    target_rows = []
    for i, row in enumerate(rows):
        columns = row.locator("td").all_inner_texts()
        if len(columns) >= 5 and "등록테스트" in columns[4]:
            target_rows.append(i)

    if not target_rows:
        print("삭제할 등록테스트 제품이 없습니다.")
        return

    # 랜덤으로 하나 선택해서 삭제
    random_row_index = random.choice(target_rows)
    delete_product_and_verify(page, row_index=random_row_index)




# 랜덤(1~3개) 제품 선택 후 일괄 삭제
def test_bulk_delete_products(browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])

    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"])
    
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr").all()
    target_rows = []
    for i, row in enumerate(rows):
        columns = row.locator("td").all_inner_texts()
        if len(columns) >= 5 and "등록테스트" in columns[4]:
            target_rows.append(i)

    if len(target_rows) < 1:
        print("삭제할 등록테스트 제품이 없습니다.")
        return

    num_to_select = min(random.randint(1, 3), len(target_rows))
    selected_rows = random.sample(target_rows, num_to_select)

    selected_product_names = []
    for idx in selected_rows:
        cell = page.locator(f"table tbody tr >> nth={idx} >> td:nth-child(1)")
        cell.click()  
        name = page.locator(f"table tbody tr >> nth={idx} >> td:nth-child(5)").inner_text().strip().splitlines()[0]
        selected_product_names.append(name)

    try:
        # page.locator("data-testid=btn_del_bulk").click()
        page.get_by_text("일괄 삭제", exact=True).click()

        alert_popup = page.locator("div[role=alertdialog]")  
        alert_popup.get_by_text("삭제", exact=True).click()

        page.wait_for_timeout(2000)
        page.reload()

        failed = []
        for name in selected_product_names:
            if not check_delete(page, name):
                failed.append(name)

        if not failed:
            msg = f"[PASS][제품관리] 제품 {len(selected_product_names)}개 일괄 삭제 성공: {selected_product_names}"
            print(msg)
        else:
            fail_msg = f"[FAIL][제품관리] 일부 제품 삭제 실패: {failed}"
            print(fail_msg)
            assert False, fail_msg

    except Exception as e:
        error_msg = f"[FAIL][제품관리] 일괄 삭제 중 예외 발생\n에러 내용: {str(e)}"
        print(error_msg)
        raise







# # 제품 삭제 테스트 (🔔테스트 아이디 부여 필요🔔)
# def find_target_rows(page):
#     target_rows = []
#     rows = page.locator("table tbody tr").all()

#     for i, row in enumerate(rows):
#         columns = row.locator("td").all_inner_texts()
#         if len(columns) >= 5 and "등록테스트" in columns[4]:
#             target_rows.append(i)

#     return target_rows

# def is_product_name_present(page, product_name: str) -> bool:
#     rows = page.locator("table tbody tr").all()
#     for row in rows:
#         columns = row.locator("td").all_inner_texts()
#         if len(columns) >= 5 and product_name in columns[4]:
#             return True
#     return False

# def test_delete_single_product(browser):
#     page = browser.new_page()
#     page.goto(URLS["bay_login"])

#     page.fill("data-testid=input_id", Account["testid"])
#     page.fill("data-testid=input_pw", Account["testpw"])
#     page.click("data-testid=btn_login")
#     page.wait_for_url(URLS["bay_home"])

#     page.goto(URLS["bay_prdList"])
#     page.wait_for_timeout(2000)

#     target_rows = find_target_rows(page)

#     if not target_rows:
#         print("삭제할 등록테스트 제품이 없습니다.")
#         return

#     random_row = random.choice(target_rows)
#     product_name = page.locator(f"table tbody tr >> nth={random_row} >> td:nth-child(5)").inner_text().strip()

#     delete_button = page.locator(f"table tbody tr >> nth={random_row} >> td:nth-child(9) button").nth(1)
#     delete_button.click()
#     page.locator("data-testid=btn_del").click()
#     page.wait_for_timeout(2000)
#     page.reload()

#     assert not is_product_name_present(page, product_name), f"❌ 제품 삭제 실패: {product_name} 이(가) 목록에 존재함"
#     print(f"[PASS] 제품 '{product_name}' 삭제 완료 및 검증 성공")

# def test_delete_multiple_products(browser):
#     page = browser.new_page()
#     page.goto(URLS["bay_login"])

#     page.fill("data-testid=input_id", Account["testid"])
#     page.fill("data-testid=input_pw", Account["testpw"])
#     page.click("data-testid=btn_login")
#     page.wait_for_url(URLS["bay_home"])

#     page.goto(URLS["bay_prdList"])
#     page.wait_for_timeout(2000)

#     target_rows = find_target_rows(page)

#     if len(target_rows) < 2:
#         print("삭제할 제품이 2개 이상 존재하지 않습니다.")
#         return

#     selected_rows = random.sample(target_rows, k=random.randint(2, len(target_rows)))

#     selected_product_names = []
#     for row_idx in selected_rows:
#         checkbox = page.locator(f"table tbody tr >> nth={row_idx} >> td:nth-child(1) input[type='checkbox']")
#         checkbox.check()
#         product_name = page.locator(f"table tbody tr >> nth={row_idx} >> td:nth-child(5)").inner_text().strip()
#         selected_product_names.append(product_name)

#     page.locator("data-testid=btn_del_bulk").click()
#     page.locator.wait_for("data-testid=btn_del")
#     page.locator("data-testid=btn_del").click()
#     page.wait_for_timeout(2000)
#     page.reload()

#     for name in selected_product_names:
#         assert not is_product_name_present(page, name), f"❌ 제품 삭제 실패: {name} 이(가) 목록에 존재함"
#     print(f"[PASS] 제품 {len(selected_product_names)}개 삭제 완료 및 검증 성공: {selected_product_names}")

    











