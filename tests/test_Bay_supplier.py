import random
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.product_utils import  find_supplier_in_paginated_list
from helpers.common_utils import bay_login 
from datetime import datetime
def generate_edit_name():
    now = datetime.now()
    return f"수정_{now.strftime('%m%d_%H%M')}"
# 업체 등록 확인 
def test_register_supplier(page):
    try:
        bay_login(page, "admin")
        
        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier = "자동화 업체명 등록 삭제 테스트용"
        manager = "매니저 이름 확인용"
        contact = "01012345678"
        memo = "자동화 테스트로 업체명 등록 확인 합니다. 바로 삭제"
        # 등록
        page.click("data-testid=btn_orderadd")
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_name", supplier)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_manager", manager)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_sup_contact", contact)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_memo", memo)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_confirm")
        expect(page.locator("data-testid=alert_register")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        found = find_supplier_in_paginated_list(page, supplier, manager, contact, memo)
        assert found, f"❌ 등록된 업체 정보가 리스트에서 확인되지 않음: {supplier}, {manager}, {contact}"
        print(f"[PASS] 업체 등록 및 리스트 확인 완료: {manager} ({contact})")
        # 수정
        page.reload()
        page.wait_for_timeout(1000)
        edit_supplier = generate_edit_name()
        new_manager = "담당자 수정"
        new_contact = "01067864545"
        new_memo = "자동화 테스트로 업체 정보 수정 확인"

        page.fill("data-testid=input_search", supplier)
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_edit").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_cancel").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_edit").click()
        page.wait_for_timeout(1000)
        
        page.fill("data-testid=input_sup_name", edit_supplier)
        page.wait_for_timeout(2000)
        page.fill("data-testid=input_sup_manager", new_manager)
        page.wait_for_timeout(2000)
        page.fill("data-testid=input_sup_contact", new_contact)
        page.wait_for_timeout(2000)
        page.fill("data-testid=input_memo", new_memo)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_confirm")
        expect(page.locator("data-testid=alert_edit")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        # 삭제
        page.fill("data-testid=input_search", edit_supplier)  # 제품명 검색
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")  # 검색 버튼 클릭
        page.wait_for_timeout(1000)

        rows = page.locator("table tbody tr")
        row_count = rows.count()

        if row_count == 0:
            print("❌ 검색 결과가 없습니다.")
            return

        # 2. 검색 결과 리스트에서  선택
        index = 0  
        selected_row = rows.nth(index)  # 랜덤으로 선택된 행
        selected_row.locator("data-testid=btn_delete").click()
        page.wait_for_timeout(1000)

        # 4. 삭제 모달에서 삭제 버튼 선택
        txt_delete = "업체를 삭제하시겠습니까?"
        expect(page.locator("data-testid=txt_delete")).to_have_text(txt_delete, timeout=3000)
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=alert_delete")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


        # 5. 리스트에서 미노출 확인
        page.goto(URLS["bay_supplier"])  # 리스트를 새로고침
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", edit_supplier) 
        page.wait_for_timeout(1000)
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
        raise

# 업체 중복값 확인  
def test_register_supplier_duplicate(page):
    try:
        bay_login(page, "admin")
        
        page.goto(URLS["bay_supplier"])
        page.wait_for_url(URLS["bay_supplier"], timeout=60000)

        supplier_name = "중복테스트"
        manager_name = "권정의"
        contact_info = "01062754153"
        
        print(f"선택된 업체: {supplier_name}, 담당자: {manager_name}, 연락처: {contact_info}")

        # 2. 선택한 업체 정보로 중복 등록 시도
        page.click("data-testid=btn_orderadd")  # 업체 등록 모달 열기
        page.wait_for_timeout(500)
        page.fill("data-testid=input_sup_name", supplier_name)  # 업체명 입력
        page.wait_for_timeout(500)
        page.fill("data-testid=input_sup_manager", manager_name)  # 담당자 입력
        page.wait_for_timeout(500)
        page.fill("data-testid=input_sup_contact", contact_info)  # 연락처 입력
        page.wait_for_timeout(500)
        page.click("data-testid=btn_confirm")  # 완료 버튼 클릭
        
        # 3. 중복 알림 확인
        expect(page.locator("data-testid=alert_duplicate")).to_be_visible(timeout=3000), "❌ 중복 알림 문구가 표시되지 않음"
        print(f"[PASS] 중복 등록 시 알림 문구 노출 확인: {supplier_name} / {manager_name}")
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_cancel").click()
        page.wait_for_timeout(1000)

        # 사용 중인 업체 삭제 불가 확인
        page.fill("data-testid=input_search", "중복테스트")  # 제품명 검색
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()  # 검색 버튼 클릭
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_delete").first.click()
        expect(page.locator("data-testid=alert_using")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)


    except Exception as e:
        raise
