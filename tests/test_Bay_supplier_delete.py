import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result

def test_delete_supplier(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        # 1. "자동화 업체명" 검색
        page.fill("data-testid=input_search", "자동화 업체명")  # 제품명 검색
        page.click("data-testid=btn_search")  # 검색 버튼 클릭
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        row_count = rows.count()

        if row_count == 0:
            print("❌ 검색 결과가 없습니다.")
            save_test_result("test_delete_supplier", "검색 결과가 없습니다.", status="FAIL")
            return

        # 2. 검색 결과 리스트에서 랜덤으로 하나 선택
        random_index = random.randint(0, row_count - 1)  # 랜덤 인덱스 생성
        selected_row = rows.nth(random_index)  # 랜덤으로 선택된 행
        manager_name = selected_row.locator("td:nth-child(2)").inner_text().strip()  # 담당자명
        print(f"선택 담당자: {manager_name}")

        # 3. 해당 매니저 이름이 있는 행에서 5번째 열의 두 번째 버튼 클릭
        if manager_name:  # 담당자 이름이 존재하면
            delete_btn = selected_row.locator("td:nth-child(5) button:nth-child(2)")
            delete_btn.click()

        # 4. 삭제 모달에서 삭제 버튼 선택
        page.locator("data-testid=btn_del").click()  # 삭제 버튼 클릭
        page.wait_for_timeout(1000)

        # 5. 리스트에서 미노출 확인
        page.goto(URLS["bay_supplier"])  # 리스트를 새로고침
        page.fill("data-testid=input_search", "자동화 업체명")  # "자동화 업체명"으로 검색
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        found = False  # 해당 항목이 있는지 여부를 체크하는 변수

        for row in rows:
            supplier_name = row.locator("td:nth-child(1)").inner_text().strip()  # 업체명
            row_manager_name = row.locator("td:nth-child(2)").inner_text().strip()  # 담당자명

            # 동일한 행에 "자동화 업체명"과 선택한 "manager_name"이 모두 있는지 확인
            if supplier_name == "자동화 업체명" and row_manager_name == manager_name:
                found = True
                break  # 해당 항목이 있으면 반복 종료

        # 만약 '자동화 업체명'과 선택한 'manager_name'이 존재하는 행이 없으면 PASS, 존재하면 FAIL
        if not found:
            print(f"[PASS] 제품 '{manager_name}' 삭제 후 리스트에서 미노출 확인 완료.")
            save_test_result("test_delete_supplier", f"제품 '{manager_name}' 삭제 후 리스트에서 미노출 확인", status="PASS")
        else:
            assert False, f"❌ 삭제 후에도 제품 '{manager_name}'이 리스트에 존재합니다。"
    
    except Exception as e:
        # 실패 시 결과를 저장하고 예외를 다시 던짐
        fail_msg = f"제품 삭제 실패: {str(e)}"
        save_test_result("test_delete_supplier", fail_msg, status="FAIL")
        raise
