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
    referrer_1 = "QA 계정"
    edit_approval = "김수연"
    edit_referrer = "김사라"

    page.locator("data-testid=input_search").fill(name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    last_cell = first_row.locator("td").last

    edit_button = last_cell.locator('[data-testid="btn_edit"]')
    edit_button.click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=3000)

    # 규칙명 수정
    page.locator("data-testid=input_rule_name").fill(edit_name)
    page.wait_for_timeout(1000)

    # 승인자 변경 (1: 권정의 > 김수연, 2: QA 계정 > 권정의 3: QA 계정)
    page.locator("data-testid=drop_approver_trigger").nth(0).click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(edit_approval)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=edit_approval).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_approver_trigger").nth(1).click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(approval_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=approval_1).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_add_approver").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_trigger").last.click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(referrer_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=referrer_1).click()
    page.wait_for_timeout(1000)
    
    # 참조자 변경 (1: QA 계정 > 김사라, 2: 권정의 > QA 계정, 3: 권정의)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_trigger").first.click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(edit_referrer)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item", has_text=edit_referrer).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_referrer_trigger").nth(1).click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(referrer_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item", has_text=referrer_1).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_add_referrer").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_trigger").last.click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(approval_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item", has_text=approval_1).click()
    page.wait_for_timeout(1000)

    # 저장 후 이름 수정 반영 확인
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_edit")).to_have_text("승인 규칙이 수정되었습니다.", timeout=3000)
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
    assert approval_text == edit_approval+" 외 2명", f"❌ 등록한 승인자 대표가 아님(등록한 값: {edit_approval}, 실제 노출 값: {approval_text})"
    page.wait_for_timeout(1000)

    referrer_cell = rows.nth(0).locator('td:nth-child(3)') # 1행 3열 (참조자)
    referrer_text = referrer_cell.inner_text()
    assert referrer_text == edit_referrer+" 외 2명", f"❌ 등록한 참조자 대표가 아님(등록한 값: {edit_referrer}, 실제 노출 값: {referrer_text})"
    page.wait_for_timeout(1000)

def test_delete_approval_rule(page:Page):
    delete_name = "[수정] 규칙 등록 테스트"

    bay_login(page)
    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("data-testid=input_search", timeout=3000)
    page.locator("data-testid=input_search").fill(delete_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    last_cell = first_row.locator("td").last

    delete_button = last_cell.locator('[data-testid="btn_delete"]')
    delete_button.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("승인 규칙을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_delete")).to_have_text("승인 규칙 삭제가 완료되었습니다.", timeout=5000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill(delete_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    
    expect(page.locator("data-testid=txt_nosearch")).to_have_text("일치하는 항목이 없습니다", timeout=5000)
    page.wait_for_timeout(1000)