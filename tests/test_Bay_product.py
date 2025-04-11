from playwright.sync_api._generated import Browser
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.save_test_result import save_test_result  




# 여러 개 제품 등록 테스트
def test_register_multiple_products(browser: Browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_prdAdd"])
        # page.click("data-testid=btn_addprd")
        page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

        num_products = 6  # 제품 총 등록 개수는 6개 고정
        for idx in range(num_products):
            # 구분 선택
            page.locator("data-testid=drop_type_trigger").last.click()
            page.wait_for_timeout(1000)
            type_items = page.locator("data-testid=drop_type_item")
            type_index = random.randint(0, type_items.count() - 1)
            selected_type = type_items.nth(type_index).inner_text().strip()
            type_items.nth(type_index).click()

            # 종류 선택
            page.locator("data-testid=drop_group_trigger").last.click()
            page.wait_for_timeout(1000)
            group_items = page.locator("data-testid=drop_group_item")
            group_index = random.randint(0, group_items.count() - 1)
            selected_group = group_items.nth(group_index).inner_text().strip()
            group_items.nth(group_index).click()
            
            # 제품명 생성 및 입력
            prdname_kor, prdname_eng = generate_product_names()
            page.locator("data-testid=input_prdname_kor").last.fill(prdname_kor)
            page.locator("data-testid=input_prdname_eng").last.fill(prdname_eng)

            prdnames=[]
            prdnames.append(prdname_kor)

            # 제조사 선택
            page.locator("data-testid=drop_maker_trigger").last.click()
            page.wait_for_timeout(1000)
            maker_items = page.locator("data-testid=drop_maker_item")
            maker_index = random.randint(0, maker_items.count() - 1)
            selected_maker = maker_items.nth(maker_index).inner_text().strip()
            maker_items.nth(maker_index).click()

            page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
            safety = 5
            page.locator("data-testid=input_stk_safe").last.fill(str(safety))
            auto_order = 10
            page.locator("data-testid=input_stk_qty").last.fill(str(auto_order))

            # 업체 선택
            page.locator("data-testid=drop_supplier_trigger").last.click()
            page.wait_for_timeout(1000)
            supplier_items = page.locator("data-testid=drop_supplier_item")
            automation_supplier = supplier_items.locator("text=자동화업체")  # 자동화 테스트 안정성을 위해 지정
            automation_supplier.click()
            

            # JSON 저장
            append_product_name(
                prdname_kor=prdname_kor,
                prdname_eng=prdname_eng,
                # supplier=automation_supplier,
                type_name=selected_type,
                group=selected_group,
                maker=selected_maker,
                safety=safety,
                auto_order=auto_order
            )

            if idx < num_products - 1:
                add_row_button = page.locator("data-testid=btn_addrow")
                add_row_button.wait_for(state="visible", timeout=5000)
                add_row_button.click(force=True)
               

        # page.click("data-testid=btn-save")
        page.locator("button:has-text('완료')").click()
        page.wait_for_timeout(1000)
        print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")

        # 제품 등록 확인: 제품 리스트
        verify_products_in_list(page, prdnames, URLS["bay_prdList"], "제품명 검색", 4)

        # 제품 등록 확인: 재고 리스트
        verify_products_in_list(page, prdnames, URLS["bay_stock"], "제품명 검색", 4)

        save_test_result("test_register_multiple_products", f"[PASS] {num_products}개 제품 등록 및 저장 완료", status="PASS")

    except Exception as e:
        print(f"[FAIL] 여러 개 제품 등록 실패: {str(e)}")
        save_test_result("test_register_multiple_products", f"[FAIL] 여러 개 제품 등록 실패: {str(e)}", status="FAIL")
        raise
