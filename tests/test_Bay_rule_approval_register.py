from playwright.sync_api import Page, expect
from helpers.common_utils import bay_login
from config import URLS

def test_approval_rules_register(page:Page):
    bay_login(page)
    page.goto(URLS["bay_approval_rule"])
    page.wait_for_timeout(2000)

    name = "규칙 등록 테스트"
    approval_1 = "권정의"
    approval_2 = "메디"
    referrer_1 = "메디"
    referrer_2 = "권정의"
    txt_register = "승인 규칙 등록이 완료되었습니다."

    page.locator("data-testid=btn_register").click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=3000)
    page.locator("data-testid=input_rule_name").fill(name)
    page.wait_for_timeout(1000)
    # 승인자 1 선택
    page.locator("data-testid=drop_approver_trigger").click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(approval_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_approver_item", has_text=approval_1).click()
    page.wait_for_timeout(1000)
    # 승인자 2 선택
    page.locator("data-testid=btn_add_approver").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_trigger").last.click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(approval_1)
        # 승인자 중복 선택 불가
    expect(page.locator("data-testid=drop_approver_item")).to_be_hidden(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_search").fill(approval_2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_approver_item", has_text=approval_2).click()
    page.wait_for_timeout(1000)
    # 참조자 1 선택
    page.locator("data-testid=drop_referrer_trigger").click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(referrer_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_referrer_item", has_text=referrer_1).click()
    page.wait_for_timeout(1000)
    # 참조자 2 선택
    page.locator("data-testid=btn_add_referrer").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_trigger").last.click()
    page.wait_for_selector("data-testid=drop_referrer_search", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(referrer_1)
        # 참조자 중복 선택 불가
    expect(page.locator("data-testid=drop_referrer_item")).to_be_hidden(timeout=3000)
    page.wait_for_timeout(1000) 
    page.locator("data-testid=drop_referrer_search").fill(referrer_2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=data-testid=drop_referrer_item", has_text=referrer_2).click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_register")).to_have_text(txt_register, timeout=3000)
    page.wait_for_timeout(1000)


    # 리스트에서 등록한 규칙 검색 후 노출 확인
    page.locator("data-testid=input_search").fill(name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)

    rows = page.locator('table tbody tr')
    name_cell = rows.nth(0).locator('td:nth-child(1)') # 1행 1열 (규칙명)
    name_text = name_cell.inner_text()
    assert name_text == name, f"❌ 등록한 승인 규칙이 리스트에 없음(등록한 값: {name}, 실제 노출 값: {name_text})"
    page.wait_for_timeout(1000)

    # 결재 라인 n명일 때 대표자 노출 확인
    approval_cell = rows.nth(0).locator('td:nth-child(2)') # 1행 2열 (승인자)
    approval_text = approval_cell.inner_text()
    assert approval_text == approval_1+" 외 1명", f"❌ 등록한 승인자 대표가 아님(등록한 값: {approval_1}, 실제 노출 값: {approval_text})"
    page.wait_for_timeout(1000)

    referrer_cell = rows.nth(0).locator('td:nth-child(3)') # 1행 3열 (참조자)
    referrer_text = referrer_cell.inner_text()
    assert referrer_text == referrer_1+" 외 1명", f"❌ 등록한 참조자 대표가 아님(등록한 값: {referrer_1}, 실제 노출 값: {referrer_text})"
    page.wait_for_timeout(1000)

