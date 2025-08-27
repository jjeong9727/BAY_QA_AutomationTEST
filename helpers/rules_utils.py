from playwright.sync_api import Page, expect

def search_and_check_rule(page: Page, rule_name: str, order_cycle:str, product:str, memo:str):
    # 검색 수행
    page.locator("data-testid=input_search").fill(rule_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    # ✅ 첫 번째 데이터 행 기준으로 검증
    row = page.locator("table tbody tr").first

    # 규칙명
    expect(row.locator("td").nth(0)).to_have_text(rule_name)

    # 발주 주기 (예: "매주 월, 수, 금 / 03:30")
    
    expect(row.locator("td").nth(1)).to_have_text(order_cycle)

    # 제품 수 (예: "0개 제품")
    expect(row.locator("td").nth(2)).to_have_text(product)

    # 메모 일부 포함되는지 확인
    expect(row.locator("td").nth(3)).to_contain_text(memo[:10])  # 앞쪽 일부만 매칭

    page.wait_for_timeout(1000)

