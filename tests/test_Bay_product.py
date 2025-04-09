from playwright.sync_api._generated import Browser
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.save_test_result import save_test_result  

# 제품 1개 등록 테스트
def test_register_product(browser: Browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])

        # 로그인
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        # 등록화면 이동
        page.goto(URLS["bay_prdList"])
        page.click("data-testid=btn_addprd")
        page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

        # 구분 선택
        page.click("data-testid=drop_type_trigger")
        page.wait_for_timeout(1000)
        type_items = page.locator("data-testid=drop_type_item")
        type_index = random.randint(0, type_items.count() - 1)
        selected_type_element = type_items.nth(type_index)
        selected_type = selected_type_element.inner_text().strip()
        selected_type_element.click()

        # 종류 선택
        page.click("data-testid=drop_group_trigger")
        page.wait_for_timeout(1000)
        group_items = page.locator("data-testid=drop_group_item")
        group_index = random.randint(0, group_items.count() - 1)
        selected_group_element = group_items.nth(group_index)
        selected_group = selected_group_element.inner_text().strip()
        selected_group_element.click()

        # 제조사 선택
        page.click("data-testid=drop_maker_trigger")
        page.wait_for_timeout(1000)
        maker_items = page.locator("data-testid=drop_maker_item")
        maker_index = random.randint(0, maker_items.count() - 1)
        selected_maker_element = maker_items.nth(maker_index)
        selected_maker = selected_maker_element.inner_text().strip()
        selected_maker_element.click()

        # 업체 선택
        page.locator("data-testid=drop_supplier").last.click()
        page.wait_for_timeout(1000)
        supplier_items = page.locator("data-testid=drop_supplier_item")
        automation_supplier = supplier_items.locator("text=자동화업체")  # 자동화 테스트 안정성을 위해 지정
        automation_supplier.click()

        # 제품명 생성 및 입력
        prdname_kor, prdname_eng = generate_product_names()
        page.fill("data-testid=input_prdname_kor", prdname_kor)
        page.fill("data-testid=input_prdname_eng", prdname_eng)

        # 단가 / 재고 / 발주 수량 입력
        safety = 5
        auto_order = 10
        page.fill("data-testid=input_price", str(random.randint(1000, 10000)))
        page.fill("data-testid=input_stk_safe", safety)
        page.fill("data-testid=input_stk_qty", auto_order)

        # 저장
        page.click("data-testid=btn-save")
        page.wait_for_timeout(1000)

        # 제품 정보 JSON 저장
        append_product_name(
            prdname_kor=prdname_kor,
            prdname_eng=prdname_eng,
            manager=automation_supplier,
            type_name=selected_type,
            group=selected_group,
            maker=selected_maker,
            safety=safety,
            auto_order=auto_order
        )

        print(f"[PASS] 제품 등록 및 저장 완료: {prdname_kor} / {automation_supplier}")
        
        # 제품 등록 확인: 제품 리스트
        verify_products_in_list(page, prdname_kor, URLS["bay_prdList"], "제품명 검색", 5)

        # 제품 등록 확인: 재고 리스트
        verify_products_in_list(page, prdname_kor, URLS["bay_stock"], "제품명 검색", 5)

        save_test_result("test_register_product", f"[PASS] 제품 등록 및 저장 완료: {prdname_kor}", status="PASS")

    except Exception as e:
        print(f"❌ 제품 등록 실패: {str(e)}")
        save_test_result("test_register_product", f"[FAIL] 제품 등록 실패: {str(e)}", status="FAIL")
        raise


# 여러 개 제품 등록 테스트
def test_register_multiple_products(browser: Browser):
    try:
        page = browser.new_page()
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"], timeout=60000)

        page.goto(URLS["bay_prdList"])
        page.click("data-testid=btn_addprd")
        page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

        num_products = 5  # 제품 총 등록 개수는 5개 고정
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

            # 제조사 선택
            page.locator("data-testid=drop_maker_trigger").last.click()
            page.wait_for_timeout(1000)
            maker_items = page.locator("data-testid=drop_maker_item")
            maker_index = random.randint(0, maker_items.count() - 1)
            selected_maker = maker_items.nth(maker_index).inner_text().strip()
            maker_items.nth(maker_index).click()

            # 업체 선택
            page.locator("data-testid=drop_supplier").last.click()
            page.wait_for_timeout(1000)
            supplier_items = page.locator("data-testid=drop_supplier_item")
            automation_supplier = supplier_items.locator("text=자동화업체")  # 자동화 테스트 안정성을 위해 지정
            automation_supplier.click()

            # 제품명 생성 및 입력
            prdname_kor, prdname_eng = generate_product_names()
            page.locator("data-testid=input_prdname_kor").last.fill(prdname_kor)
            page.locator("data-testid=input_prdname_eng").last.fill(prdname_eng)

            # 단가 / 안전 재고 / 자동 발주 수량 입력
            safety = random.randint(3, 10)
            auto_order = random.randint(1, 5)
            page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
            page.locator("data-testid=input_stk_safe").last.fill(safety)
            page.locator("data-testid=input_stk_qty").last.fill(auto_order)

            # JSON 저장
            append_product_name(
                prdname_kor=prdname_kor,
                prdname_eng=prdname_eng,
                manager=automation_supplier,
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

        page.click("data-testid=btn-save")
        page.wait_for_url(URLS["bay_prdList"], timeout=10000)
        print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")

        # 제품 등록 확인: 제품 리스트
        verify_products_in_list(page, prdname_kor, URLS["bay_prdList"], "제품명 검색", 5)

        # 제품 등록 확인: 재고 리스트
        verify_products_in_list(page, prdname_kor, URLS["bay_stock"], "제품명 검색", 5)

        save_test_result("test_register_multiple_products", f"[PASS] {num_products}개 제품 등록 및 저장 완료", status="PASS")

    except Exception as e:
        print(f"[FAIL] 여러 개 제품 등록 실패: {str(e)}")
        save_test_result("test_register_multiple_products", f"[FAIL] 여러 개 제품 등록 실패: {str(e)}", status="FAIL")
        raise
