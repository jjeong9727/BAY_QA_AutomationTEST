from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login
# from helpers.order_status_utils import search_order_history
from helpers.approve_status_data import approve_status_map
from helpers.approve_utils import (
    search_order_pending_history, check_approval_status_buttons, get_approve_id_from_approve_list
)
products = [ "자동화개별제품_1","자동화개별제품_2", "자동화개별제품_3", "수동 발주 제품 2"] #
bulk_products = [ "배치 확인 제품 2", "배치 확인 제품 3", "배치 확인 제품 5", "배치 확인 제품 6", "배치 확인 제품 8", "배치 확인 제품 9"] 
# 제품 1, 4, 7은 자동 승인이라 제외
approved_products = ["배치 확인 제품 1","배치 확인 제품 4","배치 확인 제품 7",]
reject_products = ["발주 거절 제품 1","발주 거절 제품 2","발주 거절 제품 3"] 
approval_rules = ["승인규칙_1명", "승인규칙_n명", "자동 승인"]
order_rule = ["자동화규칙_개별", "자동화규칙_묶음"] 
approver = ["qaje@medisolveai.com", "qasr@medisolveai.com", "qasy@medisolveai.com", "qa@medisolveai.com", "stg@medisolveai.com"]

# 개별 내역 승인 
def test_approve_order(page:Page):
    for product in products:
        bay_login(page, account="qaje") #로그인할 계정 
        page.goto(URLS["bay_approval"])
        page.wait_for_timeout(2000)
        if product == "수동 발주 제품 2":
            check_approval_status_buttons(page, "승인 대기(승인요청)", product, "수동 발주", bulk=False, approve=True)
        else:
            check_approval_status_buttons(page, "승인 대기(승인요청)", product, order_rule[0], bulk=False, approve=True)
        page.wait_for_timeout(2000)

        # 승인 ID 가져오기 
        approve_id = get_approve_id_from_approve_list(page, product) 
        approval_url = f"{URLS["base_approval_url"]}/{approve_id}/confirm"
        page.goto(approval_url)
        page.wait_for_selector("data-testid=btn_login", timeout=5000)

        page.locator("data-testid=input_email").fill(approver[0])
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_pw").fill(Account["testpw"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_login").click()
        expect(page.locator("data-testid=txt_name")).to_have_text("권정의 원장", timeout=7000) 
        expect(page.locator("data-testid=txt_product")).to_have_text(product, timeout=3000) 
        page.locator("data-testid=btn_approve").click()
        expect(page.locator("data-testid=toast_approve")).to_have_text("발주 승인이 완료되었습니다.", timeout=5000)
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_email").fill(approver[0])
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_pw").fill(Account["testpw"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_login").click()
        expect(page.locator("data-testid=toast_approved")).to_have_text("발주 승인 완료된 발주입니다.", timeout=3000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_approval"])
        page.wait_for_timeout(2000)
        # 승인 요청 내역
        if product == products[3]:
            check_approval_status_buttons(page, "발주 승인", product, "수동 발주", bulk=False, approve=True)
        else:
            check_approval_status_buttons(page, "발주 승인", product, order_rule[0], bulk=False, approve=True)
        # 발주 예정 내역
        page.goto(URLS["bay_order_pending"])
        page.wait_for_timeout(2000)
        if product == products[3]:
            page.wait_for_timeout(1000)
        else:
            check_approval_status_buttons(page, "승인 대기(발주예정)", product, order_rule[0], bulk=False, approve=False)

        # 2번째 승인자 결재 
        bay_login(page, account="stg")
        page.goto(URLS["bay_approval"])
        page.wait_for_timeout(2000)
        if product == products[3]:
            check_approval_status_buttons(page, "승인 대기(승인요청)", product, "수동 발주", bulk=False, approve=True)
        else:
            check_approval_status_buttons(page, "승인 대기(승인요청)", product, order_rule[0], bulk=False, approve=True)
        page.wait_for_timeout(2000)
        
        page.goto(approval_url)
        page.wait_for_selector("data-testid=btn_login", timeout=5000)

        # 이전 승인자 로그인 불가 확인
        page.locator("data-testid=input_email").fill(approver[0])
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_pw").fill(Account["testpw"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_login").click()
        expect(page.locator("data-testid=toast_approved")).to_have_text("발주 승인 완료된 발주입니다.", timeout=3000)
        page.wait_for_timeout(1000)

        # 2번째 승인자 결재 
        page.locator("data-testid=input_email").fill(approver[4])
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_pw").fill(Account["testpw"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_login").click()
        expect(page.locator("data-testid=txt_name")).to_have_text("권정의 원장", timeout=7000) 
        expect(page.locator("data-testid=txt_product")).to_have_text(product, timeout=3000) 
        page.locator("data-testid=btn_approve").click()
        expect(page.locator("data-testid=toast_approve")).to_have_text("발주 승인이 완료되었습니다.", timeout=5000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_approval"])
        page.wait_for_timeout(2000)
        # 승인 요청 내역
        check_approval_status_buttons(page, "발주 승인", product, order_rule[0], bulk=False, approve=True)
        # 발주 예정 내역
        if product == products[3]:
            continue
        else:
            page.goto(URLS["bay_order_pending"])
            page.wait_for_timeout(2000)
            check_approval_status_buttons(page, "승인 완료", product, order_rule[0], bulk=False, approve=False)

# 통합 내역 승인 (요청 내역에서 바로 승인)
def test_approve_bulk_order(page:Page):
    bay_login(page)
    for product in bulk_products:
        
        page.goto(URLS["bay_approval"])
        page.wait_for_timeout(2000)
        check_approval_status_buttons(page, "승인 대기(승인요청)", product, order_rule[1], bulk=True, approve=True)
        page.wait_for_timeout(2000)

        rows = page.locator("table tbody tr")
        test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=product)).last
        approve_button = test_row.locator("data-testid=btn_approve")
        approve_button.click()

        expect(page.locator("data-testid=txt_approve")).to_have_text("발주를 승인하시겠습니까?", timeout=5000)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=toast_approve")).to_have_text("발주 승인이 완료되었습니다.", timeout=5000)  

        # 승인 요청 내역
        check_approval_status_buttons(page, "발주 승인", product, order_rule[1], bulk=True, approve=True)
        # 발주 예정 내역
        page.goto(URLS["bay_order_pending"])
        page.wait_for_selector("data-testid=txt_product_num", timeout=10000)
        check_approval_status_buttons(page, "승인 완료", product,  order_rule[1], bulk=True, approve=False)    

# 개별 내역 한번 승인 후 거절  
def test_reject_order(page:Page):
    bay_login(page, account="qaje")
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)

    check_approval_status_buttons(page, "승인 대기(승인요청)", reject_products[1], order_rule[0], bulk=False, approve=True)
    page.wait_for_timeout(2000)
    
    rows = page.locator("table tbody tr")
    test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=reject_products[1])).last
    approve_button = test_row.locator("data-testid=btn_approve")
    approve_button.click()
    expect(page.locator("data-testid=txt_approve")).to_have_text("발주를 승인하시겠습니까?", timeout=5000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_approve")).to_have_text("발주 승인이 완료되었습니다.", timeout=5000)  

    # 승인 요청 내역
    check_approval_status_buttons(page, "발주 승인", reject_products[1], order_rule[0], bulk=False, approve=True)
    # 발주 예정 내역
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    check_approval_status_buttons(page, "승인 대기(발주예정)", reject_products[1], order_rule[0], bulk=False, approve=False)

    # 2번째 결재자 
    bay_login(page, account="stg")
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)

    check_approval_status_buttons(page, "승인 대기(승인요청)", reject_products[1], order_rule[0], bulk=False, approve=True)
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    test_row = rows.filter(has=page.locator("td:nth-child(2)", has_text=reject_products[0])).last
    approve_button = test_row.locator("data-testid=btn_reject")
    approve_button.click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("발주를 거절하시겠습니까?", timeout=5000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_reject")).to_have_text("발주 거절이 완료되었습니다.", timeout=5000)  

    # 승인 요청 내역
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)
    check_approval_status_buttons(page, "발주 거절", reject_products[1], order_rule[0], bulk=False, approve=True)
    # 발주 예정 내역
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    check_approval_status_buttons(page, "승인 거절", reject_products[1], order_rule[0], bulk=False, approve=False)

# 개별 내역 바로 거절  
def test_reject_bulk_order(page:Page):
    
    bay_login(page, account="qaje")
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)   
    check_approval_status_buttons(page, "승인 대기(승인요청)", reject_products[0], order_rule[0], bulk=False, approve=True)
    page.wait_for_timeout(2000) 
    
        # 승인 ID 가져오기 
    approve_id = get_approve_id_from_approve_list(page, reject_products[0]) 
    approval_url = f"{URLS["base_approval_url"]}/{approve_id}/confirm"
    page.goto(approval_url)
    page.wait_for_selector("data-testid=btn_login", timeout=5000)

    page.locator("data-testid=input_email").fill(approver[0])
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_pw").fill(Account["testpw"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_login").click()
    expect(page.locator("data-testid=txt_name")).to_have_text("권정의 원장", timeout=3000) 
    expect(page.locator("data-testid=txt_product")).to_have_text(reject_products[0], timeout=3000) 
    page.locator("data-testid=btn_reject").click()
    expect(page.locator("data-testid=toast_reject")).to_have_text("발주 거절이 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000) 

    # 거절 후 로그인 불가 확인 
    page.locator("data-testid=input_email").fill(approver[0])
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_pw").fill(Account["testpw"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_login").click()
    expect(page.locator("data-testid=toast_rejected")).to_have_text("발주 거절 완료된 발주입니다.", timeout=3000)
    
    # 승인 요청 내역
    page.goto(URLS["bay_approval"])
    page.wait_for_timeout(2000)
    check_approval_status_buttons(page, "발주 거절", reject_products[0], order_rule[0], bulk=False, approve=True)
    # 발주 예정 내역
    page.goto(URLS["bay_order_pending"])
    page.wait_for_timeout(2000)
    check_approval_status_buttons(page, "승인 거절", reject_products[0], order_rule[0], bulk=False, approve=False)

