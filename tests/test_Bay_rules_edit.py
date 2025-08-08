# 새로 생성한 규칙(연결 제품 없는 상태) 수정 시 "발주 규칙 변경 제품" 팝업 미노출 확인
# 실제 수정 후 수정값 반영 확인 (제품 등록 시 규칙 드롭다운 / 발주 규칙 리스트 화면)
# "규칙 연결 확인 제품"에 생성한 규칙 연결 후 수정 완료
# 발주 규칙 에서 연결 제품 확인 후 수정 시 발주 규칙 변경 제품 확인
# 등록한 제품 수정 화면으로 이동 해서 "자동화 규칙" 으로 수정
# 이후 새로 생성한 규칙 삭제까지 확인

from playwright.sync_api import Page, expect
from helpers.common_utils import bay_login
from config import URLS
from helpers.rules_utils import search_and_check_rule
MEMO_TEXT = "✔️ Memo 테스트 123!@# 한글과 English 포함하여 총 100자를 맞춘 예시입니다. 여기에 더 추가하면 100자가 딱 됩니다!!! 딱 맞아 떨어지는 100자는 여기까지이후 문자는 삭제 되어야 합니다."
rule_name_1 = "규칙명 등록 테스트_매일"
rule_name_2 = "규칙명 등록 테스트_매주"

new_name = "[수정]규칙명 등록 테스트_매주"
edit_info_1 = "매일 / 20:00"
edit_info_2 = "매주 월,수,목,금 / 16:30"
product_name = "발주 규칙 변경 제품"
def test_order_rules_edit(page:Page):
    bay_login(page)
    # 제품에 규칙 연결 후 수정 확인
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(3000)
    
    page.locator("data-testid=input_search").fill(product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(3000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    for i in range(row_count):
        edit_button = rows.nth(i).locator("td:last-child >> text=수정")
        if edit_button.is_visible():
            print(f"✅ {i}번째 행의 수정 버튼 클릭")
            edit_button.click()
            page.wait_for_timeout(2000)
            break

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill(rule_name_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_item", has_text=rule_name_1).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_stk_safe").fill("5")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_stk_qty").fill("10")
    page.wait_for_timeout(500)

    txt_edit = "제품을 수정하시겠습니까?"
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_edit")).to_have_text(txt_edit, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)

    # 첫번째 규칙 수정 (발주 규칙 변경 제품 팝업 확인)
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_search").fill(rule_name_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").first.click()
    page.wait_for_timeout(2000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator(f'div[data-testid^="drop_minute_item_"][data-value="00"]').click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=txt_title")).to_have_text("발주 규칙 변경 제품", timeout=3000)

    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit_pending")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    search_and_check_rule(page, "규칙명 등록 테스트_매일", edit_info_1, "1개 제품", MEMO_TEXT)
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)
    
    # 두번째 규칙 수정(발주 규칙 변경 제품 팝업 미노출)
    page.locator("data-testid=input_search").fill(rule_name_2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_edit").first.click()
    page.wait_for_timeout(2000)

    page.locator("data-testid=input_rule_name").fill(new_name)
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)
    dropdown_items = page.locator('div[data-testid="drop_weekday_item"] div[data-value]')
    dropdown_items.nth(3).click()
    page.wait_for_timeout(1000)


    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)

    search_and_check_rule(page, new_name, edit_info_2, "0개 제품", MEMO_TEXT)
    page.wait_for_timeout(1000)

def test_order_rules_delete(page:Page):
    bay_login(page)
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    txt_delete = "발주 규칙을 삭제하시겠습니까?"
    # 삭제 확인
    page.locator("data-testid=input_search").fill(rule_name_2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_delete").first.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text(txt_delete, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_delete")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 사용중 토스트 확인
    page.locator("data-testid=input_search").fill("자동화규칙_개별")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_delete").first.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text(txt_delete, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_using")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 제품의 규칙 수정 후 최종 삭제
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(3000)
    
    page.locator("data-testid=input_search").fill(product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(3000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    for i in range(row_count):
        edit_button = rows.nth(i).locator("td:nth-child(12) >> text=수정")
        if edit_button.is_visible():
            print(f"✅ {i}번째 행의 수정 버튼 클릭")
            edit_button.click()
            page.wait_for_timeout(2000)
            break

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_stk_safe").fill("5")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_stk_qty").fill("10")
    page.wait_for_timeout(500)

    txt_edit = "제품을 수정하시겠습니까?"
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_edit")).to_have_text(txt_edit, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    txt_delete = "발주 규칙을 삭제하시겠습니까?"
    # 삭제 확인
    page.locator("data-testid=input_search").fill(rule_name_1)
    
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_delete").first.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text(txt_delete, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_delete")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

