from socket import timeout
from playwright.sync_api import Page, expect
import random
from config import URLS, Account
from helpers.product_utils import get_latest_product_name, append_product_name, generate_product_names, verify_products_in_list, select_from_dropdown
from helpers.common_utils import bay_login

# 제품 등록 확인 
def test_register_multiple_products(page: Page):
    try:
        bay_login(page, "admin")
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
        suppliers = ["자동화업체", "자동화업체A", "자동화업체B", "자동화업체C" ] 
        managers = ["권정의 010-6275-4153", "권정의A 010-6275-4153", "권정의B 010-6275-4153", "권정의C 010-6275-4153"]

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
            auto_input.fill(str(auto_order))
            page.wait_for_timeout(1000)

            page.locator("data-testid=drop_supplier_trigger").last.click()
            page.wait_for_timeout(1000)
            
            if idx == 0: #제품1
                page.locator("data-testid=drop_supplier_search").last.fill(suppliers[1])
                page.wait_for_timeout(1000)
                page.locator("data-testid=drop_supplier_item", has_text=suppliers[1]).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(managers[1], timeout=3000)
                page.wait_for_timeout(1000)
                supplier = f"{suppliers[1]}, {managers[1]}"
            elif idx == 1: #제품2
                page.locator("data-testid=drop_supplier_search").last.fill(suppliers[2])
                page.wait_for_timeout(1000)
                page.locator("data-testid=drop_supplier_item", has_text=suppliers[2]).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(managers[2], timeout=3000)
                page.wait_for_timeout(1000)
                supplier = f"{suppliers[2]}, {managers[2]}"
            elif idx == 2: #제품3
                page.locator("data-testid=drop_supplier_search").last.fill(suppliers[3])
                page.wait_for_timeout(1000)
                page.locator("data-testid=drop_supplier_item", has_text=suppliers[3]).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(managers[3], timeout=3000)
                page.wait_for_timeout(1000)
                supplier = f"{suppliers[3]}, {managers[3]}"
            else: #제품 4, 5, 6
                page.locator("data-testid=drop_supplier_search").last.fill(suppliers[0])
                page.wait_for_timeout(1000)
                page.locator("data-testid=drop_supplier_item", has_text=suppliers[0]).click()
                expect(page.locator("data-testid=txt_supplier_contact")).to_have_text(managers[0], timeout=3000)
                page.wait_for_timeout(1000)
                supplier = f"{suppliers[0]}, {managers[0]}"

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

            # 승인 규칙 미노출 확인 
            expect(page.locator("data-testid=drop_approval_trigger")).not_to_be_visible(timeout=3000)
            
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
                "approve_rule" : "자동 승인", 
                "register": "manual"
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

        verify_products_in_list(page, prdnames, URLS["bay_prdList"], 3)

    except Exception as e:
        print(f"[FAIL] 여러 개 제품 등록 실패: {str(e)}")
        raise


# 제품 중복 값 확인 
def test_duplicate_product_name(page):
    try:
        prdname_kor = "중복테스트"
        prdname_eng = "Duplicate Test"

        bay_login(page, "admin")

        page.goto(URLS["bay_prdList"])
        expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=10000)
        page.locator("data-testid=btn_addprd").click()
        expect(page.locator("data-testid=drop_type_trigger")).to_be_visible(timeout=20000)

        # 구분 선택
        page.locator("data-testid=drop_type_trigger").last.click()
        page.wait_for_selector("data-testid=drop_type_item", timeout=3000)
        type_items = page.locator("data-testid=drop_type_item")
        type_index = random.randint(0, type_items.count() - 1)
        selected_type = type_items.nth(type_index).inner_text().strip()
        type_items.nth(type_index).click()
        page.wait_for_timeout(1000)

        # 종류 선택
        page.locator("data-testid=drop_group_trigger").last.click()
        page.wait_for_selector("data-testid=drop_group_item", timeout=3000)
        group_items = page.locator("data-testid=drop_group_item")
        group_index = random.randint(0, group_items.count() - 1)
        selected_group = group_items.nth(group_index).inner_text().strip()
        group_items.nth(group_index).click()
        page.wait_for_timeout(1000)
        
        # 제품명 생성 및 입력
        page.fill("data-testid=input_prdname_kor", prdname_kor)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_prdname_eng", prdname_eng)
        page.wait_for_timeout(1000)

        # 제조사 선택
        page.locator("data-testid=drop_maker_trigger").last.click()
        page.wait_for_selector("data-testid=drop_maker_item", timeout=3000)
        maker_items = page.locator("data-testid=drop_maker_item")
        maker_index = random.randint(0, maker_items.count() - 1)
        selected_maker = maker_items.nth(maker_index).inner_text().strip()
        maker_items.nth(maker_index).click()
        page.wait_for_timeout(1000)
        # 단가
        page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
        page.wait_for_timeout(1000)
        # 자동 발주 수량
        page.locator("data-testid=input_stk_qty").last.fill("10")
        page.wait_for_timeout(1000)
        # 안전 재고
        page.locator("data-testid=input_stk_safe").last.fill("10")
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        # 업체 선택
        page.locator("data-testid=drop_supplier_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_search").fill("중복테스트")
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_supplier_item", has_text="중복테스트").first.click()
        page.wait_for_timeout(1000)

        # 발주 규칙 선택 
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)") 
        page.wait_for_timeout(1000)
        rule = "규칙 없음"
        page.locator("data-testid=drop_rule_trigger").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_search").fill(rule)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_rule_item", has_text=rule).click()
        page.wait_for_timeout(1000)

        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_save").click()
        
        expect(page.locator("data-testid=alert_duplicate")).to_be_visible(timeout=4000)
        page.wait_for_timeout(1000)

        print(f"[PASS] 중복 제품명 확인")

    except Exception as e:
        print(f"❌ 중복 테스트 실패: {str(e)}")
        raise


