from playwright.sync_api import Page, expect
from helpers.common_utils import bay_login
from config import URLS

def test_approval_rules_register(page:Page):
    bay_login(page)
    page.goto(URLS["bay_approval_rule"])
    page.wait_for_timeout(2000)

    name = "규칙 등록 테스트"
    edit_name = "[수정] 규칙 등록 테스트"
    approval_1 = "권정의"
    referrer_1 = "메디"
    edit_approval = "김사라"
    edit_referrer = "김수연"
    txt_edit_next = "승인 규칙이 수정되었습니다. 다음 출고분부터 적용됩니다."
    txt_edit_complete = "승인 규칙이 수정되었습니다."

    page.locator("data-testid=input_search").fill(name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    # 규칙명 수정
    page.locator("data-testid=input_rule_name").fill(edit_name)
    page.wait_for_timeout(1000)

    # 승인자 참조자 추가
    page.locator("data-testid=btn_edit").first.click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=3000)
    page.locator("data-testid=btn_add_approver").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_approver_trigger").last.click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(edit_approval)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_approver_item", has_text=edit_approval).click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_add_referrer").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_referrer_trigger").click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(edit_referrer)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_referrer_item", has_text=edit_referrer).click()
    page.wait_for_timeout(1000)

    # 저장 후 이름 수정 반영 확인
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_edit")).to_have_text(txt_edit_complete, timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill(edit_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)

    rows = page.locator('table tbody tr')
    name_cell = rows.nth(0).locator('td:nth-child(1)') # 1행 1열 (규칙명)
    name_text = name_cell.inner_text()
    assert name_text == edit_name, f"❌ 등록한 승인 규칙이 리스트에 없음(등록한 값: {edit_name}, 실제 노출 값: {name_text})"
    page.wait_for_timeout(1000)

    # 결재 인원 변경 확인 
    approval_cell = rows.nth(0).locator('td:nth-child(2)') # 1행 2열 (승인자)
    approval_text = approval_cell.inner_text()
    assert approval_text == approval_1+" 외 2명", f"❌ 등록한 승인자 대표가 아님(등록한 값: {approval_1}, 실제 노출 값: {approval_text})"
    page.wait_for_timeout(1000)

    referrer_cell = rows.nth(0).locator('td:nth-child(3)') # 1행 3열 (참조자)
    referrer_text = referrer_cell.inner_text()
    assert referrer_text == referrer_1+" 외 2명", f"❌ 등록한 참조자 대표가 아님(등록한 값: {referrer_1}, 실제 노출 값: {referrer_text})"
    page.wait_for_timeout(1000)

def test_delete_approval_rule(page:Page):
    delete = "중복테스트"
    txt_delete = "승인 규칙을 삭제하시겠습니까?"
    delete_complete = "승인 규칙 삭제가 완료되었습니다."

