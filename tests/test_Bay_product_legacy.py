from playwright.sync_api._generated import Browser
import random
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list, is_product_exist

# # 제품 1개 등록 테스트
# def test_register_product(browser: Browser):
#     page = browser.new_page()
#     page.goto(URLS["bay_login"])

#     # 로그인
#     page.fill("data-testid=input_id", Account["testid"])
#     page.fill("data-testid=input_pw", Account["testpw"])
#     page.click("data-testid=btn_login")
#     page.wait_for_url(URLS["bay_home"], timeout=60000)

#     # 등록화면 이동
#     page.goto(URLS["bay_prdList"])
#     page.click("data-testid=btn_addprd")
#     page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

#     # 구분 선택
#     page.click("data-testid=drop_type_trigger")
#     page.wait_for_timeout(1000)
#     type_items = page.locator("data-testid=drop_type_item")
#     type_index = random.randint(0, type_items.count() - 1)
#     selected_type_element = type_items.nth(type_index)
#     selected_type = selected_type_element.get_attribute("data-value").strip()
#     selected_type_element.click()

#     # 종류 선택
#     page.click("data-testid=drop_category_trigger")
#     page.wait_for_timeout(1000)
#     category_items = page.locator("data-testid=drop_category_item")
#     category_index = random.randint(0, category_items.count() - 1)
#     selected_category_element = category_items.nth(category_index)
#     selected_category = selected_category_element.get_attribute("data-value").strip()
#     selected_category_element.click()

#     # 제조사 선택
#     page.click("data-testid=drop_maker_trigger")
#     page.wait_for_timeout(1000)
#     maker_items = page.locator("data-testid=drop_maker_item")
#     maker_index = random.randint(0, maker_items.count() - 1)
#     selected_maker_element = maker_items.nth(maker_index)
#     selected_maker = selected_maker_element.get_attribute("data-value").strip()
#     selected_maker_element.click()


#     # # 업체 담당자 선택
#     # page.click("data-testid=drop_supplier")
#     # page.wait_for_timeout(1000)
#     # supplier_items = page.locator("data-testid=drop_supplier_item")
#     # supplier_index = random.randint(0, supplier_items.count() - 1)
#     # selected_supplier_element = supplier_items.nth(supplier_index)
#     # selected_manager = selected_supplier_element.inner_text().strip()
#     # selected_supplier_element.click()

#     # # 연락처 선택
#     # page.click("data-testid=drop_contact")
#     # page.wait_for_timeout(1000)
#     # contact_items = page.locator("data-testid=drop_contact_item")
#     # contact_index = random.randint(0, contact_items.count() - 1)
#     # selected_contact_element = contact_items.nth(contact_index)
#     # selected_contact = selected_contact_element.inner_text().strip()
#     # selected_contact_element.click()

#     # 제품명 생성 및 입력
#     prdname_kor, prdname_eng = generate_product_names()
#     page.fill("data-testid=input_prdname_kor", prdname_kor)
#     page.fill("data-testid=input_prdname_eng", prdname_eng)

#     # # 단가 / 재고 / 발주 수량 입력
#     # safety = random.randint(3, 10)
#     # auto_order = random.randint(1, 5)
#     # page.fill("data-testid=input_price", str(random.randint(1000, 10000)))
#     # page.fill("data-testid=input_stk_safe", safety)
#     # page.fill("data-testid=input_stk_qty", auto_order)

#     # 저장
#     page.click("data-testid=btn-save")
#     page.wait_for_timeout(1000)
#     page.goto(URLS["bay_prdList"], timeout=10000)
#     page.locator('input[placeholder="제품명 검색"]').wait_for(timeout=5000)

#     # 제품 정보 JSON 저장
#     append_product_name(
#         prdname_kor=prdname_kor,
#         prdname_eng=prdname_eng,
#         # manager=selected_manager,
#         # contact=selected_contact,
#         type_name=selected_type,
#         category=selected_category,
#         maker=selected_maker,
#         # safety=safety,
#         # auto_order=auto_order
#     )

#     # print(f"[PASS] 제품 등록 및 저장 완료: {prdname_kor} / {selected_manager}")
    
#      # 제품 등록 확인: 제품 리스트
#     # verify_products_in_list(page, prdname_kor, URLS["bay_prdList"], "제품명 검색", 5)
#     assert is_product_exist(page, prdname_kor), f"❌ 제품 리스트에서 {prdname_kor} 확인 실패"
#     # # 제품 등록 확인: 재고 리스트
#     # verify_products_in_list(page, prdname_kor, URLS["bay_stock"], "제품명 검색", 5)



# # 여러 개 제품 등록 테스트
from playwright.sync_api._generated import Browser
import random
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list, is_product_exist
import time

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
        print(f"\n👉 [STEP] {idx+1}번째 제품 시작")
        step_start = time.time()

        # --- 구분 선택 ---
        type_start = time.time()
        page.locator("data-testid=drop_type_trigger").nth(idx).click()
        page.locator("data-testid=drop_type_item").first.wait_for(state="visible", timeout=5000)

        type_items = page.locator("data-testid=drop_type_item")
        type_count = type_items.count()
        type_index = random.randint(0, type_count - 1)
        selected_type = type_items.nth(type_index).get_attribute("data-value").strip()
        type_items.nth(type_index).click()
        print(f"[LOG] 구분 선택 완료 - {round(time.time() - type_start, 2)}초")

        # --- 종류 선택 ---
        category_start = time.time()
        page.locator("data-testid=drop_category_trigger").nth(idx).click()
        page.locator("data-testid=drop_category_item").first.wait_for(state="visible", timeout=5000)

        category_items = page.locator("data-testid=drop_category_item")
        category_count = category_items.count()
        category_index = random.randint(0, category_count - 1)
        selected_category = category_items.nth(category_index).get_attribute("data-value").strip()
        category_items.nth(category_index).click()
        print(f"[LOG] 종류 선택 완료 - {round(time.time() - category_start, 2)}초")

        # --- 제조사 선택 ---
        maker_start = time.time()
        page.locator("data-testid=drop_maker_trigger").nth(idx).click()
        page.locator("data-testid=drop_maker_item").first.wait_for(state="visible", timeout=5000)

        maker_items = page.locator("data-testid=drop_maker_item")
        maker_count = maker_items.count()
        maker_index = random.randint(0, maker_count - 1)
        selected_maker = maker_items.nth(maker_index).get_attribute("data-value").strip()
        maker_items.nth(maker_index).click()
        print(f"[LOG] 제조사 선택 완료 - {round(time.time() - maker_start, 2)}초")

        # --- 제품명 입력 ---
        prdname_kor, prdname_eng = generate_product_names()
        while prdname_kor in product_names:
            prdname_kor, prdname_eng = generate_product_names()
        product_names.append(prdname_kor)

        input_start = time.time()
        page.locator("data-testid=input_prdname_kor").nth(idx).wait_for(state="visible", timeout=5000)
        page.locator("data-testid=input_prdname_kor").nth(idx).fill(prdname_kor)
        page.locator("data-testid=input_prdname_eng").nth(idx).fill(prdname_eng)
        print(f"[LOG] 제품명 입력 완료 - {round(time.time() - input_start, 2)}초")

        # 전체 제품 등록 시간 출력
        print(f"✅ {idx+1}번째 제품 전체 등록 완료 - {round(time.time() - step_start, 2)}초")

        # 다음 행 추가
        if idx < num_products - 1:
            page.locator("data-testid=btn_addrow").click()

            # 다음 입력 필드가 나타날 때까지 대기
            page.locator("data-testid=input_prdname_kor").nth(idx + 1).wait_for(state="visible", timeout=7000)

    page.click("data-testid=btn-save")
    page.wait_for_timeout(1000)

    # 제품 등록 확인
    assert is_product_exist(page, product_names), "[FAIL] 제품 리스트에 일부 제품이 누락됨"
    print(f"[PASS] 등록된 {len(product_names)}개 제품 확인 완료")