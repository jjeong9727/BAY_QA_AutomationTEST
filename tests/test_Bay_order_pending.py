from playwright.sync_api import Page, expect
from config import URLS
from helpers.common_utils import bay_login
from helpers.approve_status_data import approve_status_map
from helpers.approve_utils import search_order_pending_history, check_approval_status_buttons

products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3"]
bulk_products = ["자동화제품_1", "자동화제품_2", "자동화제품_3", 
            "자동화제품_4", "자동화제품_5", "자동화제품_6", 
            "자동화제품_7", "자동화제품_8", "자동화제품_9"]
reject_products = ["발주 거절 제품 1","발주 거절 제품 2","발주 거절 제품 3"] 
delete_product = "발주 삭제 제품 1"
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
    target_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=reject_products[2])).first

    last_cell = target_row.locator("td").last

    edit_button = last_cell.locator('[data-testid="btn_edit"]').first
    edit_button.click()

    edit_cell = target_row.locator("td").nth(3).locator("input")
    qty_cell=target_row.locator("td").nth(4).locator("input")
    amount_cell=target_row.locator("td").nth(5)
    amount = amount_cell.inner_text().strip()

    edit_cell.fill("10000")
    page.wait_for_timeout(1000)
    # 최소 발주 수량 토스트 확인
    qty_cell.fill("0")
    page.wait_for_timeout(1000)
    edit_button.click()
    expect(page.locator("data-testid=toast_order_min")).to_have_text("발주 수량은 최소 1개 이상이어야 합니다.", timeout=5000)

    # 수정 중입니다 토스트 확인
    page.locator("data-testid=btn_search").click()
    expect(page.locator("data-testid=toast_editing")).to_have_text("현재 수정 중입니다.", timeout=5000)

    qty_cell.fill("10")
    page.wait_for_timeout(1000)
    edit_button.click()
    page.wait_for_timeout(1000)
    expect(edit_cell).to_have_value("10000", timeout=3000)
    assert amount == '100,000', f"금액이 다름 (기대 값: 100,000원, 노출 값: {amount}원)"

# 승인 요청 버튼 확인 후 요청 동작 (개별 내역)
def test_check_status_request(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)

    check_approval_status_buttons(page, status="승인 요청", product=products[0], 
                                  order_rule=order_rule[0], bulk=False, approve=False)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)

    for product in products:
        page.fill("data-testid=input_search", product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        page.locator("data-testid=btn_approval").first.click()
        expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_request").click()
        expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)

    

# 승인 요청 버튼 확인 후 요청 동작 (통합 내역)
def check_status_request_bulk(page:Page):
    target_products = ["자동화제품_3", "자동화제품_6", "자동화제품_9"]
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    # 승인 요청 전 상태 확인 (통합내역 / 발주 요청 내역)
    check_approval_status_buttons(page, status="승인 요청", product=bulk_products[0], 
                                  order_rule=order_rule[1], bulk=True, approve=False)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)

    # 자동화제품 승인 요청 처리 및 자동 승인 확인
    for product in target_products:
        # 제품 검색
        page.fill("data-testid=input_search", product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        # 상세 보기 클릭
        page.locator("data-testid=btn_detail").first.click()
        page.wait_for_timeout(1000)

        # 상세 행 가져오기 (2, 3, 4행)
        rows = page.locator("table tbody tr")

        for row_idx in [1, 2, 3]:  # 0이 첫 행 → 2,3,4행은 인덱스 1,2,3
            product_cell = rows.nth(row_idx).locator("td:nth-child(2)")
            approval_button = rows.nth(row_idx).locator("data-testid=btn_approval")

            product_text = product_cell.inner_text().strip()
            status_text = approval_button.inner_text().strip()
            
            print(f"📝 확인 중: {product} → {product_text}, 상태: {status_text}")

            # ✅ 상태 체크 (예: 승인 요청 or 자동 승인)
            if status_text == "승인 요청":
                page.locator("data-testid=btn_approval").nth(row_idx).click()
                expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
                page.wait_for_timeout(1000)
                page.locator("data-testid=btn_request").click()
                expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)
                page.wait_for_timeout(1000)

            elif status_text == "자동 승인":
                expect(page.locator("data-testid=btn_approval").nth(row_idx)).to_have_text("자동 승인", timeout=3000)
                expect(page.locator("data-testid=btn_approval").nth(row_idx)).to_be_disabled(timeout=3000)

        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(500)
        
# # 발주 예정 제품 삭제 
# def test_delete_history(page:Page):
#     bay_login(page)
#     page.goto(URLS["bay_order_pending"])
#     page.wait_for_timeout(2000)

#     # 삭제 전 상태 확인 
#     check_approval_status_buttons(page, status="승인 요청", product=delete_product, 
#                                 order_rule=order_rule[1], bulk=True, approve=False)
    
#     # 삭제 확인
#     rows = page.locator('table tbody tr')
#     buttons = rows.nth(1).locator("td").nth(-1)
#     # delete_button = buttons.locator("data-testid=btn_delete")
#     delete_button = buttons.locator("data-testid=btn_edit").last

#     delete_button.click()
#     expect(page.locator("data-testid=txt_delete")).to_have_text("발주 예정 제품을 삭제하시겠습니까?", timeout=3000)
#     page.locator("data-testid=btn_confirm").click()
#     expect(page.locator("data-testid=toast_delete")).to_have_text("발주 예정 제품 삭제가 완료되었습니다.", timeout=3000)
#     page.wait_for_timeout(1000)
