from playwright.sync_api import Page, expect
from helpers.common_utils import bay_login
from config import URLS
from helpers.rules_utils import search_and_check_rule

# 메모 입력값 생성
MEMO_TEXT = "✔️ Memo 테스트 123!@# 한글과 English 포함하여 총 100자를 맞춘 예시입니다. 여기에 더 추가하면 100자가 딱 됩니다!!! 딱 맞아 떨어지는 100자는 여기까지이후 문자는 삭제 되어야 합니다."

def test_order_rules_register(page: Page):
    bay_login(page)
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    rule_name_1 = "규칙명 등록 테스트_매주"
    rule_name_2 = "규칙명 등록 테스트_매일"
    # ✅ 첫 번째 규칙: 매주
    page.locator("data-testid=btn_register").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_rule_name").fill(rule_name_1)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item_1").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)
    dropdown_items = page.locator('div[data-testid="drop_weekday_item"] div[data-value]')
    count = dropdown_items.count()

    for i in range(count):
        text = dropdown_items.nth(i).inner_text().strip()
        if text in ["월요일", "수요일", "금요일"]:
            dropdown_items.nth(i).click()
            page.wait_for_timeout(1000)



    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator('div[data-testid^="drop_hour_item_"][data-value="16"]').click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator('div[data-testid^="drop_minute_item_"][data-value="30"]').click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(MEMO_TEXT)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    search_and_check_rule(page, rule_name_1, "매주 월,수,금 / 16:30", "0개 제품", MEMO_TEXT)
    page.wait_for_timeout(1000)

    # ✅ 두 번째 규칙: 매일
    page.locator("data-testid=btn_register").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_rule_name").fill(rule_name_2)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item_0").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).not_to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator('div[data-testid^="drop_hour_item_"][data-value="20"]').click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator('div[data-testid^="drop_minute_item_"][data-value="50"]').click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(MEMO_TEXT)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=3000)

    search_and_check_rule(page, rule_name_2, "매일 / 20:50", "0개 제품", MEMO_TEXT)
    page.wait_for_timeout(1000)