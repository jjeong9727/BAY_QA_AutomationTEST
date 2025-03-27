from playwright.sync_api._generated import Browser
import pytest
import requests
import os
import random
import time
import json
from datetime import datetime 
from playwright.sync_api import sync_playwright
from config import URLS, Account
from helpers.product_utils import append_product_name

# 제품 1개 등록 테스트
def test_register_product(browser: Browser):
    from helpers.product_utils import append_product_name

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
    type_options = page.locator("data-testid=drop_type_item").all_inner_texts()
    type_index = random.randint(0, len(type_options) - 1)
    selected_type = type_options[type_index]
    page.locator("data-testid=drop_type_item").nth(type_index).click()

    # 종류 선택
    page.click("data-testid=drop_category_trigger")
    page.wait_for_timeout(1000)
    category_options = page.locator("data-testid=drop_category_item").all_inner_texts()
    category_index = random.randint(0, len(category_options) - 1)
    page.locator("data-testid=drop_category_item").nth(category_index).click()

    # 제조사 선택
    page.click("data-testid=drop_maker_trigger")
    page.wait_for_timeout(1000)
    maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()
    maker_index = random.randint(0, len(maker_options) - 1)
    page.locator("data-testid=drop_maker_item").nth(maker_index).click()

    # 업체 선택
    page.click("data-testid=drop_supplier")
    page.wait_for_timeout(1000)
    supplier_options = page.locator("data-testid=drop_supplier_item").all_inner_texts()
    supplier_index = random.randint(0, len(supplier_options) - 1)
    selected_supplier = supplier_options[supplier_index]
    page.locator("data-testid=drop_supplier_item").nth(supplier_index).click()

    # 업체 연락처 선택
    page.click("data-testid=drop_contact")
    page.wait_for_timeout(1000)
    contact_options = page.locator("data-testid=drop_contact_item").all_inner_texts()
    contact_index = random.randint(0, len(contact_options) - 1)
    page.locator("data-testid=drop_contact_item").nth(contact_index).click()

    # 제품명 생성 및 저장
    prdname_kor, prdname_eng = append_product_name(supplier=selected_supplier, type_name=selected_type)
    page.fill("data-testid=input_prdname_kor", prdname_kor)
    page.fill("data-testid=input_prdname_eng", prdname_eng)

    # 단가 / 재고 정보 입력
    page.fill("data-testid=input_price", str(random.randint(1000, 10000)))
    page.fill("data-testid=input_stk_safe", "10")
    page.fill("data-testid=input_stk_qty", "20")

    try:
        page.click("data-testid=btn-save")
        page.wait_for_url(URLS["bay_prdList"], timeout=10000)
        page.reload()
        page.wait_for_timeout(3000)

        assert page.locator(f"text={prdname_kor}").is_visible()
        print(f"[PASS][제품관리] 제품 등록 성공: {prdname_kor}")

    except Exception as e:
        print(f"❌ 제품 등록 실패: {str(e)}")
        raise


# 여러 개 제품 등록 테스트
def test_register_multiple_products(browser: Browser):
    from helpers.product_utils import append_product_name

    num_products = random.randint(2, 5)
    product_data = []

    page = browser.new_page()
    page.goto(URLS["bay_login"])
    page.fill("data-testid=input_id", Account["testid"])
    page.fill("data-testid=input_pw", Account["testpw"])
    page.click("data-testid=btn_login")
    page.wait_for_url(URLS["bay_home"], timeout=60000)

    page.goto(URLS["bay_prdList"])
    page.click("data-testid=btn_addprd")
    page.wait_for_url(URLS["bay_prdAdd"], timeout=60000)

    for idx in range(num_products):
        # 구분 선택
        page.locator("data-testid=drop_type_trigger").last.click()
        page.wait_for_timeout(1000)
        type_options = page.locator("data-testid=drop_type_item").all_inner_texts()
        type_index = random.randint(0, len(type_options) - 1)
        selected_type = type_options[type_index]
        page.locator("data-testid=drop_type_item").nth(type_index).click()

        # 종류 선택
        page.locator("data-testid=drop_category_trigger").last.click()
        page.wait_for_timeout(1000)
        category_options = page.locator("data-testid=drop_category_item").all_inner_texts()
        category_index = random.randint(0, len(category_options) - 1)
        page.locator("data-testid=drop_category_item").nth(category_index).click()

        # 제조사 선택
        page.locator("data-testid=drop_maker_trigger").last.click()
        page.wait_for_timeout(1000)
        maker_options = page.locator("data-testid=drop_maker_item").all_inner_texts()
        maker_index = random.randint(0, len(maker_options) - 1)
        page.locator("data-testid=drop_maker_item").nth(maker_index).click()

        # 업체 선택
        page.locator("data-testid=drop_supplier").last.click()
        page.wait_for_timeout(1000)
        supplier_options = page.locator("data-testid=drop_supplier_item").all_inner_texts()
        supplier_index = random.randint(0, len(supplier_options) - 1)
        selected_supplier = supplier_options[supplier_index]
        page.locator("data-testid=drop_supplier_item").nth(supplier_index).click()

        # 업체 연락처 선택
        page.locator("data-testid=drop_contact").last.click()
        page.wait_for_timeout(1000)
        contact_options = page.locator("data-testid=drop_contact_item").all_inner_texts()
        contact_index = random.randint(0, len(contact_options) - 1)
        page.locator("data-testid=drop_contact_item").nth(contact_index).click()

        # 제품명 생성 및 저장
        prdname_kor, prdname_eng = append_product_name(supplier=selected_supplier, type_name=selected_type)
        page.locator("data-testid=input_prdname_kor").last.fill(prdname_kor)
        page.locator("data-testid=input_prdname_eng").last.fill(prdname_eng)

        # 단가 / 재고 정보 입력
        page.locator("data-testid=input_price").last.fill(str(random.randint(1000, 10000)))
        page.locator("data-testid=input_stk_safe").last.fill("10")
        page.locator("data-testid=input_stk_qty").last.fill("20")

        product_data.append(prdname_kor)

        if idx < num_products - 1:
            add_row_button = page.locator("data-testid=btn_addrow")
            add_row_button.wait_for(state="visible", timeout=5000)
            add_row_button.click(force=True)

    try:
        page.click("data-testid=btn-save")
        page.wait_for_url(URLS["bay_prdList"], timeout=10000)
        page.reload()
        page.wait_for_timeout(3000)

        for name_kor in product_data:
            assert page.locator(f"text={name_kor}").is_visible(), f"❌ 등록된 제품 미확인: {name_kor}"

        page.goto(URLS["bay_stock"])
        page.wait_for_url(URLS["bay_stock"], timeout=10000)
        page.wait_for_timeout(2000)

        for name_kor in product_data:
            stock_match = page.locator("table tbody tr td:nth-child(5)", has_text=name_kor)
            assert stock_match.is_visible(), f"❌ 재고관리 목록에서 {name_kor} 미확인"

        
        

        print(f"[PASS][제품관리] {num_products}개 제품 등록 성공")

    except Exception as e:
        print(f"❌ 다중 제품 등록 실패: {str(e)}")
        raise