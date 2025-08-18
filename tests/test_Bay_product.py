from playwright.sync_api import Page, expect
import random
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list, select_from_dropdown
from helpers.common_utils import bay_login

# 드롭다운 내 검색 추가 (prep으로 등록한 값 활용)
# 저장 버튼 testid 추가

def test_register_multiple_products(page: Page):
    try:
        bay_login(page)
        page.goto(URLS["bay_prdList"])
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_addprd").click()
        page.wait_for_timeout(1000)

        num_products = 3
        prdnames = []
        prd_data = []

        type_options = ["의약품", "의료기기", "소모품"]
        group_options = ["주사제", "연고", "보톡스"]
        maker_options = ["메디톡스", "루트로닉", "휴메딕스"]
        supplier_1 = "자동화업체, 권정의A" 
        supplier_2 = "자동화업체, 권정의B"
        supplier_3 = "자동화업체, 권정의C"
        supplier_4 = "자동화업체, 권정의"

        for idx in range(num_products):
            page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            selected_type = select_from_dropdown(
                page, "drop_type_trigger", "drop_type_search", "drop_type_item", random.choice(type_options))

            selected_group = select_from_dropdown(
                page, "drop_group_trigger", "drop_group_search", "drop_group_item", random.choice(group_options))


            page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            # 제품명 입력 
            prdname_kor, prdname_eng = generate_product_names()     
            name_kor_input = page.locator("data-testid=input_prdname_kor").last
            name_kor_input.fill(prdname_kor)
            page.wait_for_timeout(1000)

            name_eng_input = page.locator("data-testid=input_prdname_eng").last
            name_eng_input.fill(prdname_eng)
            page.wait_for_timeout(1000)

            prdnames.append(prdname_kor)

            selected_maker = select_from_dropdown(
                page, "drop_maker_trigger", "drop_maker_search", "drop_maker_item", random.choice(maker_options))

            price_input = page.locator("data-testid=input_price").last
            price_input.fill(str(random.randint(1000, 10000)))
            page.wait_for_timeout(1000)

 
           # 안전 재고 / 자동 발주 수량 입력 
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

            page.locator("data-testid=drop_supplier_trigger").last.click()
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_supplier_search").last.fill("자동화업체")
            page.wait_for_timeout(1000)
            if idx == 0: #제품1
                txt_manager = "권정의A 010-6275-4153"
                supplier = supplier_1 + " 010-6275-4153"
                page.locator("data-testid=drop_supplier_item_2", has_text=supplier_1).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
                page.wait_for_timeout(1000)
            elif idx == 1: #제품2
                txt_manager = "권정의B 010-6275-4153"
                supplier = supplier_2 + " 010-6275-4153"
                page.locator("data-testid=drop_supplier_item_3", has_text=supplier_2).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
                page.wait_for_timeout(1000)
            elif idx == 2: #제품3
                txt_manager = "권정의C 010-6275-4153"
                supplier = supplier_3 + " 010-6275-4153"
                page.locator("data-testid=drop_supplier_item_4", has_text=supplier_3).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
                page.wait_for_timeout(1000)
            else: #제품 4, 5, 6
                txt_manager = "권정의 010-6275-4153"
                supplier = supplier_4 + " 010-6275-4153"
                page.locator("data-testid=drop_supplier_item_1", has_text=supplier_4).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(txt_manager, timeout=3000)
                page.wait_for_timeout(1000)

            # 발주 규칙 선택
            rule = "자동화규칙_개별"
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_rule_trigger").click()
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_rule_search").fill(rule)
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_rule_item", has_text=rule).click()
            page.wait_for_timeout(1000)

            # 승인 규칙 선택
            approve_rule = "승인규칙_n명"
            page.locator("data-testid=drop_approval_trigger").click()
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_approval_search").fill(approve_rule)
            page.wait_for_timeout(1000)
            page.locator("data-testid=drop_approval_item", has_text=approve_rule).click()
            page.wait_for_timeout(1000)
            
            prd_data.append({
                "prdname_kor": prdname_kor,
                "prdname_eng": prdname_eng,
                "type_name": selected_type,
                "group": selected_group,
                "maker": selected_maker,
                "safety": safety,
                "auto_order": auto_order,
                "order_rule": rule,
                "supplier" : supplier, # ("자동화업체, 권정의 010-6275-4153")
                "approve_rule" : approve_rule, # (승인규칙_1명)

            })

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

        for product in prd_data:
            append_product_name(**product)

        verify_products_in_list(page, prdnames, URLS["bay_prdList"], 4)
        # verify_products_in_list(page, prdnames, URLS["bay_stock"], 4)

    except Exception as e:
        print(f"[FAIL] 여러 개 제품 등록 실패: {str(e)}")
        raise
