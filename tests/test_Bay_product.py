from playwright.sync_api import Page
import random
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.common_utils import bay_login


def test_register_multiple_products(page: Page):
    try:
        bay_login(page)

        page.goto(URLS["bay_prdAdd"])
        page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

        num_products = 6
        prdnames = []
        prd_data = []

        for idx in range(num_products):
            # 구분 선택
            type_trigger = page.locator("data-testid=drop_type_trigger").last
            type_trigger.scroll_into_view_if_needed()
            type_trigger.click()
            page.wait_for_timeout(1000)
            type_items = page.locator("data-testid=drop_type_item")
            type_index = random.randint(0, type_items.count() - 1)
            selected_type = type_items.nth(type_index).inner_text().strip()
            type_items.nth(type_index).click()

            # 종류 선택
            group_trigger = page.locator("data-testid=drop_group_trigger").last
            group_trigger.scroll_into_view_if_needed()
            group_trigger.click()
            page.wait_for_timeout(1000)
            group_items = page.locator("data-testid=drop_group_item")
            group_index = random.randint(0, group_items.count() - 1)
            selected_group = group_items.nth(group_index).inner_text().strip()
            group_items.nth(group_index).click()

            # 제품명 생성 및 입력
            prdname_kor, prdname_eng = generate_product_names()
            name_kor_input = page.locator("data-testid=input_prdname_kor").last
            name_kor_input.scroll_into_view_if_needed()
            name_kor_input.fill(prdname_kor)

            name_eng_input = page.locator("data-testid=input_prdname_eng").last
            name_eng_input.scroll_into_view_if_needed()
            name_eng_input.fill(prdname_eng)

            prdnames.append(prdname_kor)

            # 제조사 선택
            maker_trigger = page.locator("data-testid=drop_maker_trigger").last
            maker_trigger.scroll_into_view_if_needed()
            maker_trigger.click()
            page.wait_for_timeout(1000)
            maker_items = page.locator("data-testid=drop_maker_item")
            maker_index = random.randint(0, maker_items.count() - 1)
            selected_maker = maker_items.nth(maker_index).inner_text().strip()
            maker_items.nth(maker_index).click()

            # 단가
            price_input = page.locator("data-testid=input_price").last
            price_input.scroll_into_view_if_needed()
            price_input.fill(str(random.randint(1000, 10000)))

            # 안전 재고 / 자동 발주 수량
            safety = 5
            auto_order = 10

            safe_input = page.locator("data-testid=input_stk_safe").last
            safe_input.scroll_into_view_if_needed()
            safe_input.fill(str(safety))

            auto_input = page.locator("data-testid=input_stk_qty").last
            auto_input.scroll_into_view_if_needed()
            auto_input.fill(str(auto_order))

            # 업체 선택
            
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)  # 스크롤 애니메이션 대기
            supplier_trigger = page.locator("data-testid=drop_supplier_trigger").last
            supplier_trigger.scroll_into_view_if_needed()
            supplier_trigger.click()
            page.wait_for_timeout(1000)
            supplier_items = page.locator("data-testid=drop_supplier_item")
            automation_supplier = supplier_items.locator("text=자동화업체")
            automation_supplier.click()
            page.wait_for_timeout(1000)


            # 나중에 저장할 데이터 보관
            prd_data.append({
                "prdname_kor": prdname_kor,
                "prdname_eng": prdname_eng,
                "type_name": selected_type,
                "group": selected_group,
                "maker": selected_maker,
                "safety": safety,
                "auto_order": auto_order
            })

            if idx < num_products - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.scroll_into_view_if_needed()
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)

        # 저장 버튼 클릭
        save_btn = page.locator("button:has-text('완료')")
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        page.wait_for_timeout(1000)
        print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")

        # JSON 파일에 한 번에 저장
        for product in prd_data:
            append_product_name(**product)

        # 등록 확인
        verify_products_in_list(page, prdnames, URLS["bay_prdList"], "제품명 검색", 4)
        verify_products_in_list(page, prdnames, URLS["bay_stock"], "제품명 검색", 4)

    except Exception as e:
        print(f"[FAIL] 여러 개 제품 등록 실패: {str(e)}")
        raise
