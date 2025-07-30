import pytest
import random
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login
from helpers.product_utils import select_from_dropdown, generate_product_name



def test_prep_bay (page:Page):
    bay_login(page)

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
        {"name": "자동화업체", "manager": "권정의", "contact": "01062754153"},
        {"name": "자동화업체A", "manager": "권정의", "contact": "01062754153"},
        {"name": "자동화업체A", "manager": "메디솔브", "contact": "01085148780"},
        {"name": "자동화업체B", "manager": "권정의", "contact": "01062754153"},
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

    

    # 발주 규칙명 "중복테스트", "자동화규칙" 등록 
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)
    rule_name = "중복테스트"
    rule_name1 = "자동화규칙"
    memo = "자동화 테스트를 위한 발주 규칙"

    page.locator("data-testid=btn_register").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_rule_name").fill(rule_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item", has_text="매일").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_item",has_text="12").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_item", has_text="00").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_register").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_rule_name").fill(rule_name1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item", has_text="매일").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_item",has_text="12").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_item", has_text="00").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)

    # 제품 등록 (중복테스트)
    page.goto(URLS["bay_products"])
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_prdadd")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_type_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_type_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_category_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_category_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_category_item", has_text="중복테스트").click()
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

    page.fill("data-testid=input_price", 100)
    page.wait_for_timeout(1000)

    # 발주 규칙 선택 추가
    rule = "규칙 없음"
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger", has_text=rule).click()
    page.wait_for_timeout(1000)
    # 규칙 없음 선택 시 비활성화 및 0 입력 상태 확인
    expect(page.locator("data-testid=input_stk_safe")).to_have_text("0",timeout=3000)
    expect(page.locator("data-testid=input_stk_safe")).to_be_visible(timeout=3000)
    expect(page.locator("data-testid=input_stk_qty")).to_have_text("0",timeout=3000)
    expect(page.locator("data-testid=input_stk_qty")).to_be_visible(timeout=3000)

    page.locator("data-testid=drop_supplier_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    # "중복테스트" 제품 등록
    page.locator("data-testid=btn_addrow").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_type_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_type_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_category_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_category_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_category_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_prdname_kor").last.fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_prdname_eng").last.fill("Duplicate Test")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_maker_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_maker_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_price").last.fill(100)
    page.wait_for_timeout(1000)

    # 발주 규칙 선택 추가
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill(rule)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger", has_text=rule).click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_stk_safe").last.fill(5)
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_stk_qty").last.fill(10)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_supplier_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    page.wait_for_timeout(1000)

    # 중복테스트 재고 등록(삭제 불가 확인용)
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

    # 배치 발주 테스트용 제품 생성(9개)
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_addprd").click()
    page.wait_for_timeout(2000)

    num_products = 9
    supplier_1 = "자동화업체A"
    supplier_2 = "자동화업체A"
    supplier_3 = "자동화업체B"
    manager1 = "권정의 010-6275-4153"
    manager2 = "메디솔브 010-8514-8780" 
    manager3 = "권정의 010-6275-4153"
    prdnames = []
    type_options = ["의약품"]
    group_options = ["보톡스"]
    maker_options = ["메디톡스"]
    
    for idx in range(num_products):
        select_from_dropdown(page, "drop_type_trigger", "drop_type_search", "drop_type_item", random.choice(type_options))
        select_from_dropdown(page, "drop_group_trigger", "drop_group_search", "drop_group_item", random.choice(group_options))
        prdname_kor, prdname_eng = generate_product_name(idx)
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

        # 발주 규칙 선택
        rule = "자동화규칙"
        page.locator("data-testid=drop_rule_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_search").fill(rule)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_trigger", has_text=rule).click()
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
        adjusted_idx = idx + 1
        if 1 <= adjusted_idx <= 3:
            txt_manager = manager1
            txt_supplier = supplier_1
        elif 4 <= adjusted_idx <= 6:
            txt_manager = manager2 
            txt_supplier = supplier_2
        elif 7 <= adjusted_idx <= 9:
            txt_manager = manager3
            txt_supplier = supplier_3
        else:
            raise ValueError(f"지원되지 않는 idx: {idx}")
        
        supplier_info = f"{txt_supplier}, {txt_manager}"
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_search").last.fill(txt_supplier)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_item", has_text=supplier_info).click()
        expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
        page.wait_for_timeout(1000)

        if idx < num_products - 1:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.scroll_into_view_if_needed()
            add_row_button.wait_for(state="visible", timeout=5000)
            add_row_button.click(force=True)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)  # 스크롤 애니메이션 대기    
    save_btn = page.locator("data-testid=btn_save")
    save_btn.scroll_into_view_if_needed()
    save_btn.click()
    page.wait_for_timeout(1000)
    print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")
