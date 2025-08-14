from playwright.sync_api import Page, expect
from config import URLS
from helpers.common_utils import bay_login
from helpers.approve_status_data import approve_status_map
from helpers.approve_utils import search_order_pending_history, check_approval_status_buttons

products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3"]
bulk_products = ["자동화제품_1", "자동화제품_2", "자동화제품_3", 
            "자동화제품_4", "자동화제품_5", "자동화제품_6", 
            "자동화제품_7", "자동화제품_8", "자동화제품_9"]
reject_products = ["발주 거절 제품_1","발주 거절 제품_2","발주 거절 제품_3"] 
delete_product = "발주 삭제 제품_1"
approval_rules = ["승인규칙_1명", "승인규칙_n명", "자동 승인"]
order_rule = ["자동화규칙_개별", "자동화규칙_묶음"]
approver = ["qaje@medisolveai.com", "qasr@medisolveai.com", "qasy@medisolveai.com", "qa@medisolveai.com", "stg@medisolveai.com"]

# 발주 예정 내역 수정 
def test_edit_history_bulk(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    
    # 발주 거절 제품_3 수정 
    search_order_pending_history(page, order_rule[1], reject_products[2])
    rows = page.locator('table tbody tr')
    first_row = rows.nth(0)
    last_cell = first_row.locator("td").last

    edit_button = last_cell.locator('[data-testid="btn_edit"]')
    edit_button.click()

    edit_cell = first_row.locator("td").nth(3)
    qty_cell=first_row.locator("td").nth(4)
    amount_cell=first_row.locator("td").nth(5)
    amount = amount_cell.inner_text().strip()

    page.locator(edit_cell).fill("10000")
    page.wait_for_timeout(1000)
    # 최소 발주 수량 토스트 확인
    page.locator(qty_cell).fill("0")
    page.wait_for_timeout(1000)
    edit_button.click()
    expect(page.locator("data-testid=toast_order_min")).to_have_text("발주 수량은 최소 1개 이상이어야 합니다.", timeout=5000)

    # 수정 중입니다 토스트 확인
    page.locator("data-testid=btn_search").click()
    expect(page.locator("data-testid=btn_search")).to_have_text("현재 수정 중입니다.", timeout=5000)

    page.locator(qty_cell).fill("10")
    page.wait_for_timeout(1000)
    edit_button.click()
    expect(edit_cell).to_have_text("10,000", timeout=3000)
    assert amount == '100,000', f"금액이 다름 (기대 값: 100,000원, 노출 값: {amount}원)"

# 승인 요청 버튼 확인 후 요청 동작 
def check_status_request_bulk(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    # 승인 요청 전 상태 확인 (통합내역 / 발주 요청 내역)
    check_approval_status_buttons(page, status="승인 요청", product=bulk_products[0], 
                                  order_rule=order_rule[1], bulk=True, approve=False)
    # 자동화제품 승인 요청 처리 및 자동 승인 확인
    for idx, product in enumerate(bulk_products, start=1):
        if idx == 9 :
            break
        search_order_pending_history(page, order_rule[1], bulk_products[0])
        page.locator("data-testid=btn_detail").first.click()

        rows = page.locator('table tbody tr')
        status_cell = rows.locator('td:nth-child(8)')
        status_text = status_cell.inner_text().strip()
            
        for i in rows:
            if status_text == "승인 요청":
                page.locator("data-testid=btn_approval").nth(i).click()
                expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
                txt_rule = f"승인 규칙명: {approval_rules[0]}"
                expect(page.locator("data-testid=txt_rule")).to_have_text(txt_rule, timeout=3000)
                page.locator("data-testid=btn_request").click()
                expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)
            elif status_text == "자동 승인":
                expect(page.locator("data-testid=btn_approval").nth(i)).to_have_text("자동 승인", timeout=3000)
                expect(page.locator("data-testid=btn_approval").nth(i)).to_be_disabled(timeout=3000)

# 발주 예정 제품 삭제 
def test_delete_history(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)

    # 삭제 전 상태 확인 
    check_approval_status_buttons(page, status="승인 요청", product=delete_product, 
                                order_rule=order_rule[1], bulk=False, approve=False)
    
    # 삭제 확인
    rows = page.locator('table tbody tr')
    buttons = rows.nth(1).locator("td").nth(-1)
    delete_button = buttons.locator("data-testid=btn_delete")

    delete_button.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("발주 예정 제품을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_delete")).to_have_text("발주 예정 제품 삭제가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)
