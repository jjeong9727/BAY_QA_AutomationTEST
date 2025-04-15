import random
from playwright.sync_api import Page
from config import URLS, Account

def test_delete_supplier(browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
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
        page.locator("data-testid=btn_confirm").click()  # 삭제 버튼 클릭
        page.wait_for_timeout(1000)

        # 5. 리스트에서 미노출 확인
        page.goto(URLS["bay_supplier"])  # 리스트를 새로고침
        page.fill("data-testid=input_search", "자동화 업체명")  # "자동화 업체명"으로 검색
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        found = False  # 해당 항목이 있는지 여부를 체크하는 변수

        for i in range(rows.count()):
            row_text = rows.nth(i).inner_text()
            if "자동화 업체명" in row_text:
                found = True
                break

        if found:
            print("❌ 삭제 실패: 여전히 목록에 남아있음")
        else:
            print("✅ 삭제 성공")
    
    except Exception as e:
        # 실패 시 결과를 저장하고 예외를 다시 던짐
        fail_msg = f"제품 삭제 실패: {str(e)}"
        raise
