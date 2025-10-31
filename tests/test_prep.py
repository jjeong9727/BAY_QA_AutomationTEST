import pytest
import random
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login
from helpers.product_utils import select_from_dropdown, generate_product_name

def test_prep_category_and_supplier (page:Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_category"])
    page.wait_for_timeout(1000)

    # 구분 등록
    page.click("data-testid=tab_type")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("의약품")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medications")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("의료기기")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medical Devices")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("소모품")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Consumables")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 종류 등록 
    page.click("data-testid=tab_category")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("주사제")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("injection")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("연고")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("ointment")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("보톡스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("botox")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 제조사 등록 
    page.click("data-testid=tab_maker")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("메디톡스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medytox")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("루트로닉")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Lutronic")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("휴메딕스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Humedix")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 업체 등록 
    # 업체 등록 정보 리스트
    suppliers = [
        {"name": "중복테스트", "manager": "권정의", "contact": "01062754153"},
        {"name": "자동화업체", "manager": "권정의", "contact": "01062754153"},
        {"name": "자동화업체A", "manager": "권정의A", "contact": "01062754153"},
        {"name": "자동화업체B", "manager": "권정의B", "contact": "01062754153"},
        {"name": "자동화업체C", "manager": "권정의C", "contact": "01062754153"},
        {"name": "자동화업체D", "manager": "권정의D", "contact": "01062754153"},
        {"name": "자동화업체E", "manager": "권정의E", "contact": "01062754153"},
        {"name": "자동화업체F", "manager": "권정의F", "contact": "01062754153"},
        {"name": "자동화업체G", "manager": "권정의G", "contact": "01062754153"},
        {"name": "자동화업체H", "manager": "권정의H", "contact": "01062754153"},
    ]

    # 등록 페이지 진입
    page.goto(URLS["bay_supplier"])
    page.wait_for_timeout(1000)

    # 업체 반복 등록
    for supplier in suppliers:
        page.click("data-testid=btn_orderadd")  # 업체 등록 모달 열기
        page.wait_for_timeout(500)

        page.fill("data-testid=input_sup_name", supplier["name"])       # 업체명
        page.fill("data-testid=input_sup_manager", supplier["manager"]) # 담당자
        page.fill("data-testid=input_sup_contact", supplier["contact"]) # 연락처

        page.click("data-testid=btn_confirm")  # 등록 완료
        page.wait_for_timeout(1000)


def test_prep_register_rules (page:Page):
    bay_login(page, "jekwon")

    # 승인 규칙 등록
    page.goto(URLS["bay_approval_rule"])
    page.wait_for_timeout(1000)

    rule1 = "승인규칙_1명"
    rule2 = "승인규칙_n명"
    name1 = "권정의"
    name2 = "황우디" 

    # 승인 규칙 1(승인자/참조자 1명)
    page.wait_for_selector("[data-testid=\'btn_register\']",timeout=5000)
    page.locator("data-testid=btn_register").click()

    page.wait_for_selector("[data-testid=\'input_rule_name\']",timeout=5000)
    page.locator("data-testid=input_rule_name").fill(rule1)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_approver_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_approver_search\']",timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=name1).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_referrer_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_referrer_search\']", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item",has_text=name1).click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)

    # 승인 규칙 2(승인자/참조자 n명)
    page.locator("data-testid=btn_register").click()

    page.wait_for_selector("[data-testid=\'input_rule_name\']",timeout=5000)
    page.locator("data-testid=input_rule_name").fill(rule2)
    page.wait_for_timeout(1000)
    # 승인자 선택
    page.locator("data-testid=drop_approver_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_approver_search\']",timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=name1).click()
    page.wait_for_timeout(1000)
    # 승인자 추가
    page.locator("data-testid=btn_add_approver").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_trigger").last.click()
    page.wait_for_selector("[data-testid=\'drop_approver_search\']",timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(name2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=name2).click()
    page.wait_for_timeout(1000)
    # 참조자 선택
    page.locator("data-testid=drop_referrer_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_referrer_search\']", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(name2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item",has_text=name2).click()
    page.wait_for_timeout(1000)

    # 참조자 추가
    page.locator("data-testid=btn_add_referrer").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_trigger").last.click()
    page.wait_for_selector("[data-testid=\'drop_referrer_search\']", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item",has_text=name1).click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)
    
    # "중복테스트"승인 규칙 
    page.wait_for_selector("[data-testid=\'btn_register\']",timeout=5000)
    page.locator("data-testid=btn_register").click()

    page.wait_for_selector("[data-testid=\'input_rule_name\']",timeout=5000)
    page.locator("data-testid=input_rule_name").fill("중복테스트")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_approver_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_approver_search\']",timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=name1).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_referrer_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_referrer_search\']", timeout=3000)
    page.locator("data-testid=drop_referrer_search").fill(name2)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_referrer_item",has_text=name2).click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_register")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)

    # 발주 규칙 등록 
    # "중복테스트", "자동화규칙_개별", "자동화규칙_묶음" 등록 
    bay_login(page, "admin")
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    rule_names = ["중복테스트", "자동화규칙_개별", "자동화규칙_묶음"]
    memo = "자동화 테스트를 위한 발주 규칙"
    hour_text = "12"
    minute_text = "00"

    for rule_name in rule_names:
        page.locator("data-testid=btn_register").click()
        page.wait_for_timeout(2000)
        page.locator("data-testid=input_rule_name").fill(rule_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_cycle_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_cycle_1").click()
        page.wait_for_timeout(1000)

        current_hour = page.locator("data-testid=drop_hour_trigger").text_content()
        if current_hour != hour_text:
            page.locator("data-testid=drop_hour_trigger").click()
            page.wait_for_timeout(1000)
            page.locator(f"data-testid=drop_hour_{hour_text}").click()
            page.wait_for_timeout(1000)


        page.locator("data-testid=drop_minute_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_minute_1").click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_memo").fill(memo)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

def test_prep_product (page:Page):
    bay_login(page, "admin")
    # 수동 발주 제품 / 발주 승인 거절 테스트용 제품 등록 
    # (수동 발주 제품_1, 2, 3 / 발주 거절 제품_1, 2, 3)
    names = ["수동 발주 제품 1", "수동 발주 제품 2", "수동 발주 제품 3", "발주 거절 제품 1", "발주 거절 제품 2", "발주 거절 제품 3"]
    
    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("[data-testid=\'btn_addprd\']", timeout=5000)
    page.locator("data-testid=btn_addprd").click()
    page.wait_for_selector("[data-testid=\'drop_type_trigger\']", timeout=3000)

    for idx, name in enumerate(names, start=1):
        page.locator("data-testid=drop_type_trigger").last.click()
        page.wait_for_timeout(1000)
        page.fill("data-testid=drop_type_search", "중복테스트")
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=drop_group_trigger").last.click()
        page.wait_for_timeout(1000)
        page.fill("data-testid=drop_group_search", "중복테스트")
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_group_item", has_text="중복테스트").click()
        page.wait_for_timeout(1000)

        page.fill("data-testid=input_prdname_kor", name)
        page.wait_for_timeout(1000)

        page.locator("data-testid=drop_maker_trigger").last.click()
        page.wait_for_timeout(1000)
        page.fill("data-testid=drop_maker_search", "중복테스트")
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=input_price").last.fill("100")

        safety = 5
        auto_order = 10

        safe_input = page.locator("data-testid=input_stk_safe").last
        safe_input.scroll_into_view_if_needed()
        safe_input.fill(str(safety))
        page.wait_for_timeout(1000)

        auto_input = page.locator("data-testid=input_stk_qty").last
        auto_input.scroll_into_view_if_needed()
        auto_input.fill(str(auto_order))
        page.wait_for_timeout(1000)

        page.wait_for_timeout(1000)
        supplier_1 = "자동화업체D, 권정의D"
        supplier_2 = "자동화업체G, 권정의G"
        supplier_3 = "자동화업체H, 권정의H"
        # 업체
        page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_trigger").last.click()
        page.wait_for_timeout(1000)

        if idx in (1, 3): #수동 발주 제품 1, 2, 3
            txt_manager = "권정의D 010-6275-4153"
            page.fill("data-testid=drop_supplier_search", "자동화업체D")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text=supplier_1).click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)
        elif idx in (4, 6): # 발주 거절 제품 1, 3
            txt_manager = "권정의G 010-6275-4153"
            page.fill("data-testid=drop_supplier_search", "자동화업체G")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text=supplier_2).click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)
        elif idx == 5: # 발주 거절 제품 2
            txt_manager = "권정의H 010-6275-4153"
            page.fill("data-testid=drop_supplier_search", "자동화업체H")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text=supplier_3).click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)
        

                # 발주 규칙 선택
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        if idx in (1, 2, 3): #수동 발주 제품 1, 2, 3
            rule = "규칙 없음" #수동 발주
        elif idx in (4, 5): # 발주 거절 제품 1, 2
            rule = "자동화규칙_개별"
        elif idx == 6: # 발주 거절 제품 3
            rule = "자동화규칙_묶음"

        page.locator("data-testid=drop_rule_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_search").fill(rule)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_item", has_text=rule).click()
        page.wait_for_timeout(1000)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        if idx < len(names) - 1:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.scroll_into_view_if_needed()
            add_row_button.wait_for(state="visible", timeout=5000)
            add_row_button.click(force=True)

        # 저장
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_save").click()
        page.wait_for_timeout(1000)
    
    # 제품 등록 (중복테스트)
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_addprd")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_type_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_type_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_group_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_group_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_group_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.fill("data-testid=input_prdname_kor", "중복테스트")
    page.wait_for_timeout(1000)
    page.fill("data-testid=input_prdname_eng", "Duplicate Test")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_maker_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_maker_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.fill("data-testid=input_price", "100")
    page.wait_for_timeout(1000)

    safety = 5
    auto_order = 10

    safe_input = page.locator("data-testid=input_stk_safe").last
    safe_input.scroll_into_view_if_needed()
    safe_input.fill(str(safety))
    page.wait_for_timeout(1000)

    auto_input = page.locator("data-testid=input_stk_qty").last
    auto_input.scroll_into_view_if_needed()
    auto_input.fill(str(auto_order))
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)


            # 발주 규칙 선택 
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    rule = "규칙 없음"
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_item", has_text=rule).click()
    page.wait_for_timeout(1000)
            # 규칙 없음 선택 시 비활성화 및 0 입력 상태 확인
    page.locator("data-testid=drop_supplier_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
            
        # 제품추가 (발주 규칙 변경 제품)
    page.locator("data-testid=btn_addrow").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_type_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_type_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_group_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_group_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_group_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_prdname_kor").last.fill("발주 규칙 변경 제품")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_prdname_eng").last.fill("ChangeRules Product")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_maker_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_maker_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_price").last.fill("100")
    page.wait_for_timeout(1000)

    safety = 5
    auto_order = 10

    safe_input = page.locator("data-testid=input_stk_safe").last
    safe_input.scroll_into_view_if_needed()
    safe_input.fill(str(safety))
    page.wait_for_timeout(1000)

    auto_input = page.locator("data-testid=input_stk_qty").last
    auto_input.scroll_into_view_if_needed()
    auto_input.fill(str(auto_order))
    page.wait_for_timeout(1000)
    
    page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
            # 발주 규칙 선택 추가
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    rule = "규칙 없음"
    page.locator("data-testid=drop_rule_trigger").last.click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_item", has_text=rule).click()
    page.wait_for_timeout(1000)
            # 규칙 없음 선택 시 비활성화 및 0 입력 상태 확인
    page.locator("data-testid=drop_supplier_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

        # 저장 
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)

        # 배치 발주 테스트용 제품 생성(9개)("배치 확인 제품 1, 2, 3, ...")
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_addprd").click()
    page.wait_for_timeout(2000)

    num_products = 9

    prdnames = []
    type_options = ["의약품"]
    group_options = ["보톡스"]
    maker_options = ["메디톡스"]
    
    for idx in range(num_products):
        select_from_dropdown(page, "drop_type_trigger", "drop_type_search", "drop_type_item", random.choice(type_options))
        select_from_dropdown(page, "drop_group_trigger", "drop_group_search", "drop_group_item", random.choice(group_options))
        
        page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        prdname_kor, prdname_eng = generate_product_name(idx+1)
        name_kor_input = page.locator("data-testid=input_prdname_kor").last
        name_kor_input.scroll_into_view_if_needed()
        name_kor_input.fill(prdname_kor)
        page.wait_for_timeout(1000)

        name_eng_input = page.locator("data-testid=input_prdname_eng").last
        name_eng_input.scroll_into_view_if_needed()
        name_eng_input.fill(prdname_eng)
        page.wait_for_timeout(1000)
        prdnames.append(prdname_kor)
        select_from_dropdown(page, "drop_maker_trigger", "drop_maker_search", "drop_maker_item", random.choice(maker_options))

        price_input = page.locator("data-testid=input_price").last
        price_input.scroll_into_view_if_needed()
        price_input.fill(str(random.randint(1000, 10000)))
        page.wait_for_timeout(1000)



        safety = 5
        auto_order = 10

        safe_input = page.locator("data-testid=input_stk_safe").last
        safe_input.scroll_into_view_if_needed()
        safe_input.fill(str(safety))
        page.wait_for_timeout(1000)

        auto_input = page.locator("data-testid=input_stk_qty").last
        auto_input.scroll_into_view_if_needed()
        auto_input.fill(str(auto_order))
        page.wait_for_timeout(1000)
        # 발주 규칙 선택
        page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        rule = "자동화규칙_묶음"
        page.locator("data-testid=drop_rule_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_search").fill(rule)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_item", has_text=rule).click()
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        
        # 업체 선택 
        page.locator("data-testid=drop_supplier_trigger").last.click()
        page.wait_for_timeout(1000)
        

        if 0 <= idx <=2: #제품1, 2, 3
            txt_manager = "권정의D 010-6275-4153"
            page.locator("data-testid=drop_supplier_search").last.fill("자동화업체D")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text="자동화업체D").click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)

        elif 3<= idx <= 5: #제품 4, 5, 6
            txt_manager = "권정의E 010-6275-4153"
            page.locator("data-testid=drop_supplier_search").last.fill("자동화업체E")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text="자동화업체E").click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)
        elif 6<= idx <= 8: #제품 7, 8, 9
            txt_manager = "권정의F 010-6275-4153"
            page.locator("data-testid=drop_supplier_search").last.fill("자동화업체F")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_item", has_text="자동화업체F").click()
            expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
            page.wait_for_timeout(1000)


                
        if idx < num_products - 1:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.scroll_into_view_if_needed()
            add_row_button.wait_for(state="visible", timeout=5000)
            add_row_button.click(force=True)
        # 저장
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)  # 스크롤 애니메이션 대기    
        save_btn = page.locator("data-testid=btn_save")
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        page.wait_for_timeout(1000)
        print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")


def test_prep_stock (page:Page):
    # 중복테스트 재고 등록(삭제 불가 확인용)
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stockadd"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.get_by_role("option", name="입고", exact=True).click()

    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    
    page.fill("data-testid=input_qty", str(3))
    page.wait_for_timeout(1000)
    page.fill("data-testid=input_memo", "테스트 메모")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(3000)


    


