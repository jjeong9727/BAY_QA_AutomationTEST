from playwright.sync_api._generated import Browser
import random
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, is_all_products_exist, is_product_exist

# 제품 1개 등록 테스트
def test_register_product(browser: Browser):
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
    selected_type = selected_type_element.get_attribute("data-value").strip()
    selected_type_element.click()

    # 종류 선택
    page.click("data-testid=drop_category_trigger")
    page.wait_for_timeout(1000)
    category_items = page.locator("data-testid=drop_category_item")
    category_index = random.randint(0, category_items.count() - 1)
    selected_category_element = category_items.nth(category_index)
    selected_category = selected_category_element.get_attribute("data-value").strip()
    selected_category_element.click()

    # 제조사 선택
    page.click("data-testid=drop_maker_trigger")
    page.wait_for_timeout(1000)
    maker_items = page.locator("data-testid=drop_maker_item")
    maker_index = random.randint(0, maker_items.count() - 1)
    selected_maker_element = maker_items.nth(maker_index)
    selected_maker = selected_maker_element.get_attribute("data-value").strip()
    selected_maker_element.click()


    # # 업체 담당자 선택
    # page.click("data-testid=drop_supplier")
    # page.wait_for_timeout(1000)
    # supplier_items = page.locator("data-testid=drop_supplier_item")
    # supplier_index = random.randint(0, supplier_items.count() - 1)
    # selected_supplier_element = supplier_items.nth(supplier_index)
    # selected_manager = selected_supplier_element.inner_text().strip()
    # selected_supplier_element.click()

    # # 연락처 선택
    # page.click("data-testid=drop_contact")
    # page.wait_for_timeout(1000)
    # contact_items = page.locator("data-testid=drop_contact_item")
    # contact_index = random.randint(0, contact_items.count() - 1)
    # selected_contact_element = contact_items.nth(contact_index)
    # selected_contact = selected_contact_element.inner_text().strip()
    # selected_contact_element.click()

    # 제품명 생성 및 입력
    prdname_kor, prdname_eng = generate_product_names()
    page.fill("data-testid=input_prdname_kor", prdname_kor)
    page.fill("data-testid=input_prdname_eng", prdname_eng)

    # # 단가 / 재고 / 발주 수량 입력
    # safety = random.randint(3, 10)
    # auto_order = random.randint(1, 5)
    # page.fill("data-testid=input_price", str(random.randint(1000, 10000)))
    # page.fill("data-testid=input_stk_safe", safety)
    # page.fill("data-testid=input_stk_qty", auto_order)

    # 저장
    page.click("data-testid=btn-save")
    page.wait_for_timeout(1000)
    page.goto(URLS["bay_prdList"], timeout=10000)
    page.locator('input[placeholder="제품명 검색"]').wait_for(timeout=5000)

    # 제품 정보 JSON 저장
    append_product_name(
        prdname_kor=prdname_kor,
        prdname_eng=prdname_eng,
        # manager=selected_manager,
        # contact=selected_contact,
        type_name=selected_type,
        category=selected_category,
        maker=selected_maker,
        # safety=safety,
        # auto_order=auto_order
    )

    # print(f"[PASS] 제품 등록 및 저장 완료: {prdname_kor} / {selected_manager}")
    
     # 제품 등록 확인: 제품 리스트
    # verify_products_in_list(page, prdname_kor, URLS["bay_prdList"], "제품명 검색", 5)
    assert is_product_exist(page, prdname_kor), f"❌ 제품 리스트에서 {prdname_kor} 확인 실패"
    # # 제품 등록 확인: 재고 리스트
    # verify_products_in_list(page, prdname_kor, URLS["bay_stock"], "제품명 검색", 5)



# 여러 개 제품 등록 테스트
def test_register_multiple_products(browser: Browser):
    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.click("data-testid=btn_addprd")
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    num_products = random.randint(2, 3)
    product_names = []
    for idx in range(num_products):
        # 구분 선택
        page.locator("data-testid=drop_type_trigger").last.click
        page.wait_for_timeout(1000)
        type_items = page.locator("data-testid=drop_type_item")
        type_index = random.randint(0, type_items.count() - 1)
        selected_type_element = type_items.nth(type_index)
        selected_type = selected_type_element.get_attribute("data-value").strip()
        selected_type_element.click()

        # 종류 선택
        page.locator("data-testid=drop_category_trigger").last.click
        page.wait_for_timeout(1000)
        category_items = page.locator("data-testid=drop_category_item")
        category_index = random.randint(0, category_items.count() - 1)
        selected_category_element = category_items.nth(category_index)
        selected_category = selected_category_element.get_attribute("data-value").strip()
        selected_category_element.click()

        # 제조사 선택
        page.locator("data-testid=drop_maker_trigger").last.click
        page.wait_for_timeout(1000)
        maker_items = page.locator("data-testid=drop_maker_item")
        maker_index = random.randint(0, maker_items.count() - 1)
        selected_maker_element = maker_items.nth(maker_index)
        selected_maker = selected_maker_element.get_attribute("data-value").strip()
        selected_maker_element.click()

        # # 업체 선택
        # page.locator("data-testid=drop_supplier").last.click()
        # page.wait_for_timeout(1000)
        # supplier_items = page.locator("data-testid=drop_supplier_item")
        # supplier_index = random.randint(0, supplier_items.count() - 1)
        # selected_manager = supplier_items.nth(supplier_index).inner_text().strip()
        # supplier_items.nth(supplier_index).click()

        # # 연락처 선택
        # page.locator("data-testid=drop_contact").last.click()
        # page.wait_for_timeout(1000)
        # contact_items = page.locator("data-testid=drop_contact_item")
        # contact_index = random.randint(0, contact_items.count() - 1)
        # selected_contact = contact_items.nth(contact_index).inner_text().strip()
        # contact_items.nth(contact_index).click()

        # 제품명 생성 및 입력
        
        while True:
            prdname_kor, prdname_eng = generate_product_names()
            if prdname_kor not in product_names:
                break
        product_names.append(prdname_kor)

        page.locator("data-testid=input_prdname_kor").last.fill(prdname_kor)
        page.locator("data-testid=input_prdname_eng").last.fill(prdname_eng)

        # JSON 저장
        append_product_name(
            prdname_kor=prdname_kor,
            prdname_eng=prdname_eng,
            # manager=selected_manager,
            # contact=selected_contact,
            type_name=selected_type,
            category=selected_category,
            maker=selected_maker,
            # safety=safety,
            # auto_order=auto_order
        )
        
        if idx < num_products - 1:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.wait_for(state="visible", timeout=5000)
            add_row_button.click(force=True)
            page.wait_for_timeout(500)
            
        

        # # 단가 / 안전 재고 / 자동 발주 수량 입력
        # safety = random.randint(3, 10)
        # auto_order = random.randint(1, 5)
        # page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
        # page.locator("data-testid=input_stk_safe").last.fill(safety)
        # page.locator("data-testid=input_stk_qty").last.fill(auto_order)

        

        

    page.click("data-testid=btn-save")
    page.goto(URLS["bay_prdList"], timeout=10000)
    page.locator('input[placeholder="제품명 검색"]').wait_for(timeout=5000)
    print(f"[PASS][제품관리] {num_products}개 제품 등록 및 저장 완료")

    # 제품 등록 확인: 제품 리스트
    # verify_products_in_list(page, prdname_kor, URLS["bay_prdList"], "제품명 검색", 5)
    assert is_all_products_exist(page, product_names), f"❌ 등록된 제품 중 일부 확인 실패"

    print(f"[PASS] 등록된 {len(product_names)}개 제품 확인 완료")
    # # 제품 등록 확인: 재고 리스트
    # verify_products_in_list(page, prdname_kor, URLS["bay_stock"], "제품명 검색", 5)


    
