from playwright.sync_api import Page, expect
from config import URLS
from helpers.common_utils import bay_login
from datetime import datetime
from helpers.approve_status_data import approve_status_map
from helpers.approve_utils import search_order_pending_history, check_approval_status_buttons, check_approval_history

products = ["자동화개별제품_1", "자동화개별제품_2", "자동화개별제품_3"] #
bulk_products = ["배치 확인 제품 1", "배치 확인 제품 2", "배치 확인 제품 3", 
            "배치 확인 제품 4", "배치 확인 제품 5", "배치 확인 제품 6", 
            "배치 확인 제품 7", "배치 확인 제품 8", "배치 확인 제품 9"]
target_products = ["배치 확인 제품 3", "배치 확인 제품 6", "배치 확인 제품 9"]
approve_time_products = ["배치 확인 제품 2", "배치 확인 제품 3","배치 확인 제품 5", "배치 확인 제품 6", "배치 확인 제품 8", "배치 확인 제품 9"]
edit_product = "발주 거절 제품 3"
delete_product = "발주 삭제 제품 1"
reject_product = ["발주 거절 제품 1", "발주 거절 제품 2"]
approval_rules = ["승인규칙_1명", "승인규칙_n명", "자동 승인"]
order_rule = ["자동화규칙_개별", "자동화규칙_묶음"]
approver = ["qaje@medisolveai.com", "qasr@medisolveai.com", "qasy@medisolveai.com", "qa@medisolveai.com", "stg@medisolveai.com"]

# 발주 예정 내역 수정 및 거절 제품 요청
def test_edit_history_bulk(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    
    # 발주 거절 제품_3 수정 
    search_order_pending_history(page, order_rule[1], edit_product)
    rows = page.locator('table tbody tr')
    target_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=edit_product)).last

    last_cell = target_row.locator("td").last

    edit_button = last_cell.locator('[data-testid="btn_edit"]').first
    edit_button.click()

    edit_cell = target_row.locator("td").nth(3).locator("input")
    qty_cell=target_row.locator("td").nth(4).locator("input")
    amount_cell=target_row.locator("td").nth(5)
    
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
    expect(page.locator("data-testid=toast_edit")).to_have_text("발주 예정 내역 수정이 완료되었습니다.",timeout=3000)
    page.wait_for_timeout(3000)
    target_cell = target_row.locator("td").nth(5)
    expect(target_cell).to_have_text("100,000", timeout=3000)

    for product in reject_product:
        search_order_pending_history(page, order_rule[0], product)

        rows = page.locator('table tbody tr')
        target_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=edit_product)).last
        target_row.locator("data-testid=btn_approval").click()

        expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
        page.locator("data-testid=btn_request").click()
        expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)

# 승인 요청 버튼 확인 후 요청 동작 (개별 내역)
def test_check_status_request(page:Page):
    bay_login(page)
    
    request_times = {}
    for product in products:
        # 요청 전 상태 확인 
        page.goto(URLS["bay_order_pending"])
        page.wait_for_timeout(2000)
        check_approval_status_buttons(page, status="승인 요청", product=product, 
                                    order_rule=order_rule[0], bulk=False, approve=False)
        page.locator("data-testid=btn_approval").last.click()
        expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
        page.wait_for_timeout(1000)


        page.locator("data-testid=btn_request").click()
        expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)
                # 현재 시간 저장 (제품 별로)
        now_str = datetime.now().strftime("%Y. %m. %d %H:%M")
        request_times[product] = now_str
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)

        # 요청 후 상태 확인 (발주 요청 내역)
        check_approval_status_buttons(page, status="승인 대기(발주예정)", product=product, order_rule=order_rule[0], bulk=False, approve=False)
        # 요청 후 상태 확인 (승인 요청 내역)
        page.goto(URLS["bay_approval"])
        page.wait_for_selector("data-testid=history", timeout=10000)
        check_approval_history(page, "승인 대기", product, auto=False, rule=order_rule[0], time = request_times[product])
        

# 승인 요청 버튼 확인 후 요청 동작 (통합 내역)
def test_check_status_request_bulk(page:Page):
    
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    # 승인 요청 전 상태 확인 (통합내역 / 발주 요청 내역)
    check_approval_status_buttons(page, status="승인 요청", product=target_products[0], 
                                  order_rule=order_rule[1], bulk=True, approve=False)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)
    request_times = {}
    # 자동화제품 승인 요청 처리 및 자동 승인 확인
    for product in target_products:
        # 제품 검색
        page.fill("data-testid=input_search", product)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        # 상세 보기 클릭
        page.locator("data-testid=btn_detail").last.click()
        page.wait_for_timeout(3000)

        # 상세 행 가져오기 (2, 3, 4행)
        rows = page.locator("table tbody tr")
        row_count = rows.count()
        # 마지막 3개 행만 선택
        last_three_idx = [row_count - 3, row_count - 2, row_count - 1]
        product_texts = []
        # 각 행의 제품명 모아서
        for row_idx in last_three_idx:
            product_cell = rows.nth(row_idx).locator("td:nth-child(2)")
            product_texts.append(product_cell.inner_text().strip())
        # 제품 리스트에 있는지 확인 
        assert set(product_texts).issubset(set(bulk_products)), \
            f"❌ 예상 외 제품 발견: {product_texts}"
        print(f"✅ 마지막 3개 행 제품명 확인 완료: {product_texts}")
        
        # 상세 내역 상태 별 승인 동작 확인 
        for row_idx in last_three_idx:
            product_cell = rows.nth(row_idx).locator("td:nth-child(2)")
            approval_button = rows.nth(row_idx).locator("data-testid=btn_approval")

            product_text = product_cell.inner_text().strip()
            status_text = approval_button.inner_text().strip()
            print(f"📝 확인 중: {product_text}, 상태: {status_text}")

            if status_text == "승인 요청":
                approval_button.click()
                expect(page.locator("data-testid=txt_approval")).to_have_text("발주 승인을 요청하시겠습니까?", timeout=3000)
                page.locator("data-testid=btn_request").click()
                expect(page.locator("data-testid=toast_request")).to_have_text("발주 승인 요청이 완료되었습니다.", timeout=3000)
                # 현재 시간 저장 (제품 별로)
                now_str = datetime.now().strftime("%Y. %m. %d %H:%M")
                request_times[product_text] = now_str            
            elif status_text == "자동 승인":
                expect(approval_button).to_have_text("자동 승인", timeout=3000)
                expect(approval_button).to_be_disabled(timeout=3000)
                request_times[product_text] = None

        # 검색 초기화
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000)
    # 승인 요청 내역 확인 (버튼 상태는 승인 요청 내역 테스트에서 )
    page.goto(URLS["bay_approval"])
    page.wait_for_selector("data-testid=history", timeout=10000)
    for product in approve_time_products:
        check_approval_history(page, "승인 대기", product, auto=False, rule=order_rule[1], time=request_times[product])
        
# 발주 예정 제품 삭제 
def test_delete_history(page:Page):
    bay_login(page)
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)

    # 삭제 전 상태 확인 
    check_approval_status_buttons(page, status="승인 요청", product=delete_product, 
                                order_rule=order_rule[1], bulk=True, approve=False)
    
    # 삭제 확인
    rows = page.locator('table tbody tr')
    test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=delete_product)).last
    delete_button = test_row.locator("data-testid=btn_edit").nth(1)

    delete_button.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("발주 예정 제품을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_delete")).to_have_text("발주 예정 제품 삭제가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)
