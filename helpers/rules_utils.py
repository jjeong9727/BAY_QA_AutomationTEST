from playwright.sync_api import Page, expect

def search_and_check_rule(page: Page, rule_name: str, order_cycle:str, product:str, memo:str):
    page.locator("data-testid=input_search").fill(rule_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    expect(page.locator("table >> tr >> nth=0 >> td >> nth=0")).to_have_text(rule_name, timeout=3000)
    expect(page.locator("table >> tr >> nth=0 >> td >> nth=1")).to_have_text(order_cycle, timeout=3000)
    expect(page.locator("table >> tr >> nth=0 >> td >> nth=1")).to_have_text(product, timeout=3000)
    expect(page.locator("table >> tr >> nth=0 >> td >> nth=3")).to_have_text(memo, timeout=3000)
    page.wait_for_timeout(1000)

