# 지점의 제품 관리 에서는 등록 불가
# 수정은 승인 규칙만 가능
# 제품 삭제 / 복구 기능 추가
from playwright.sync_api import Page, expect
import random
import json
from pathlib import Path
from config import URLS, Account
from helpers.product_utils import check_rule_for_products, edit_approval_rules_and_check
from helpers.common_utils import bay_login

PRODUCT_FILE_PATH = Path("product_name.json")
def get_register_product(register_type: str):
    with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)
    return [
        p for p in products
        if p.get("order_flag") == 0
        and p.get("stock_qty", 0) == 0
        and p.get("register") == register_type
    ]

def get_register_excel_product():
    return get_register_product("excel")

def get_register_manual_product():
    return get_register_product("manual")

excel_products = get_register_excel_product()
register_products = get_register_manual_product()
delete_products = ["삭제 복구 확인 제품 1", "삭제 복구 확인 제품 2", "삭제 복구 확인 제품 3"] 
order_rule = "자동화규칙_개별"
approve_rule = "승인규칙_1명"
all_products = excel_products + register_products
order_num_text = ""
approve_num_text = ""

# 발주, 승인 규칙 확인 및 수정 
def test_edit_approval_rule(page: Page):
    bay_login(page, "jekwon")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_download", timeout=5000)
    
    # 발주 규칙 확인 (11열, json의 order_rule 사용)
    check_rule_for_products(page, all_products, col_index=11, expected_key="order_rule", label="발주 규칙")

    # 승인 규칙 확인 (12열, 기대 값은 항상 '자동 승인')
    check_rule_for_products(page, all_products, col_index=12, expected_key=None, label="승인 규칙")

    # 승인 규칙 수정 후 반영 확인
    edit_approval_rules_and_check(page, all_products)

# 제품 삭제
def test_delete_products(page:Page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_download", timeout=5000)
    # 개별 삭제 
    for product in register_products:
  
        page.locator("data-testid=input_search").fill(product["kor"])
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        rows = page.locator("table tbody tr")
        first_row = rows.nth(0)
        delete_button = first_row.locator("td:last-child >> text=삭제")
        delete_button.click()
        expect(page.locator("data-testid=txt_delete")).to_have_text("제품을 삭제하시겠습니까?", timeout=3000)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=toast_delete")).to_have_text("제품 삭제가 완료되었습니다.", timeout=3000)
        page.wait_for_timeout(1000)

        # 삭제 버튼 > 복구 버튼으로 변경 및 버튼 활성화 확인 
        edit_button = page.locator(f"table tbody tr >> nth=0 >> td:last-child button").nth(0)
        restore_button = page.locator(f"table tbody tr >> nth=0 >> td:last-child button").nth(1)
        restore_text = restore_button.inner_text().strip()
        assert restore_text == "복구", f"복구 버튼으로 변경되지 않음 {restore_text}"
        expect(edit_button).to_be_enabled(timeout=3000)
        expect(restore_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)
        


    # 일괄 삭제 
        # 삭제 전 규칙 적용 제품 수 확인 (발주 규칙, 승인 규칙)
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("data-testid=btn_register", timeout=5000)
    page.locator("data-testid=input_search").fill(order_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    global order_num_text, approve_num_text
    rows = page.locator("table tbody tr")
    order_num_cell = rows.nth(0).locator("td:nth-child(3)")
    order_num_text = order_num_cell.inner_text().strip()

    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("data-testid=btn_register", timeout=5000)
    page.locator("data-testid=input_search").fill(approve_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
    approve_num_text = approve_num_cell.inner_text().strip()

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_download", timeout=5000)
    page.locator("data-testid=input_search").fill("삭제 복구 확인 제품")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    if row_count == 0:
        print("⚠️ 검색 결과가 없습니다.")
        return

    for i in range(row_count):
        first_cell = rows.nth(i).locator("td:nth-child(1)")
        first_cell.click()
        page.wait_for_timeout(500)  # 클릭 후 대기
        print(f"✅ {i+1}번째 행의 1열 클릭 완료")

    page.locator("data-testid=btn_del_bulk").click()
    expect(page.locator("data-testid=txt_delete_bulk")).to_have_text("3개의 제품을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_restore")).to_have_text("3개의 제품 삭제가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    # 삭제 버튼 > 복구 버튼으로 변경 및 버튼 활성화 확인 
    for i in range(row_count):
        edit_button = page.locator(f"table tbody tr >> nth={i} >> td:last-child button").nth(0)
        restore_button = page.locator(f"table tbody tr >> nth={i} >> td:last-child button").nth(1)
        restore_text = restore_button.inner_text().strip()
        assert restore_text == "복구", f"복구 버튼으로 변경되지 않음 {restore_text}"
        expect(edit_button).to_be_enabled(timeout=3000)
        expect(restore_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)


        # 재고관리 리스트 미노출 확인
        page.goto(URLS["bay_stock"])
        page.wait_for_selector("data-testid=btn_btn_stockadd")

        page.locator("data-testid=input_search").fill(delete_products[i])
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        expect(page.locator("data-testid=txt_nosearch")).to_have_text("일치하는 항목이 없습니다", timeout=5000)
        
        # 재고 등록, 수동 발주 미노출 확인
        page.locator("data-testid=btn_order").click()
        page.wait_for_selector("data-testid=drop_prdname_trigger", timeout=5000)
        page.locator("data-testid=drop_prdname_trigger").click()
        page.wait_for_selector("data-testid=drop_prdname_search", timeout=3000)
        page.locator("data-testid=drop_prdname_search").fill(delete_products[i])
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=drop_prdname_item")).to_be_hidden(timeout=3000)
        page.locator("data-testid=btn_back").click()
        page.wait_for_selector("data-testid=btn_stockadd", timeout=5000)
        page.locator("data-testid=btn_stockadd").click()
        page.wait_for_selector("data-testid=drop_prdname_trigger",timeout=5000)
        page.locator("data-testid=drop_prdname_trigger").click()
        page.wait_for_selector("data-testid=drop_prdname_search", timeout=3000)
        page.locator("data-testid=drop_prdname_search").fill(delete_products[i])
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=drop_prdname_item")).to_be_hidden(timeout=3000)

        # 적용 제품 수 확인 (발주 규칙: -1, 승인 규칙: 유지)
        page.goto(URLS["bay_rules"])
        page.wait_for_selector("data-testid=btn_register", timeout=5000)
        page.locator("data-testid=input_search").fill(order_rule)  
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        rows = page.locator("table tbody tr")
        new_order_num_cell = rows.nth(0).locator("td:nth-child(3)")
        new_order_num_text = new_order_num_cell.inner_text().strip()

        page.goto(URLS["bay_approval_rule"])
        page.wait_for_selector("data-testid=btn_register", timeout=5000)
        page.locator("data-testid=input_search").fill(approve_rule)  
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        rows = page.locator("table tbody tr")
        new_approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
        new_approve_num_text = new_approve_num_cell.inner_text().strip()


        assert order_num_text != new_order_num_text, "발주 규칙 적용 제품 수 변경 없음"
        assert approve_num_text == new_approve_num_text, "승인 규칙 적용 제품 수 유지되지 않음"
        

# 제품 복구
def test_restore_products(page:Page):
    bay_login(page, "jekwon")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_download", timeout=5000)
    # 개별 복구
    for product in register_products:
        page.locator("data-testid=input_search").fill(product["kor"])
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(2000)

        rows = page.locator("table tbody tr")
        first_row = rows.nth(0)
        restore_button = first_row.locator("td:last-child >> text=복구")
        restore_button.click()
        expect(page.locator("data-testid=txt_restore")).to_have_text("제품을 복구하시겠습니까?", timeout=3000)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=toast_restore")).to_have_text("제품 복구가 완료되었습니다.", timeout=3000)
        page.wait_for_timeout(1000)

        # 복구 버튼 > 삭제 버튼으로 변경 및 버튼 활성화 확인 
        edit_button = page.locator(f"table tbody tr >> nth=0 >> td:last-child button").nth(0)
        delete_button = page.locator(f"table tbody tr >> nth=0 >> td:last-child button").nth(1)
        delete_text = delete_button.inner_text().strip()
        assert delete_text == "복구", f"복구 버튼으로 변경되지 않음 {delete_text}"
        expect(edit_button).to_be_enabled(timeout=3000)
        expect(delete_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)

    # 일괄 복구
    page.locator("data-testid=input_search").fill("삭제 복구 확인 제품")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    if row_count == 0:
        print("⚠️ 검색 결과가 없습니다.")
        return

    for i in range(row_count):
        first_cell = rows.nth(i).locator("td:nth-child(1)")
        first_cell.click()
        page.wait_for_timeout(500)  # 클릭 후 대기
        print(f"✅ {i+1}번째 행의 1열 클릭 완료")

    page.locator("data-testid=btn_restore_bulk").click()
    expect(page.locator("data-testid=txt_restore")).to_have_text("3개의 제품을 복구하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_restore")).to_have_text("3개의 제품 복구가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    # 복구 버튼 > 삭제 버튼으로 변경 및 버튼 활성화 확인 
    for i in range(row_count):
        edit_button = page.locator(f"table tbody tr >> nth={i} >> td:last-child button").nth(0)
        delete_button = page.locator(f"table tbody tr >> nth={i} >> td:last-child button").nth(1)
        delete_text = delete_button.inner_text().strip()
        assert delete_text == "삭제", f"삭제 버튼으로 변경되지 않음 {delete_text}"
        expect(edit_button).to_be_enabled(timeout=3000)
        expect(restore_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)


        # 적용 제품 수 확인 
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("data-testid=btn_register", timeout=5000)
    page.locator("data-testid=input_search").fill(order_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_order_num_cell = rows.nth(0).locator("td:nth-child(3)")
    new_order_num_text = new_order_num_cell.inner_text().strip()

    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("data-testid=btn_register", timeout=5000)
    page.locator("data-testid=input_search").fill(approve_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
    new_approve_num_text = new_approve_num_cell.inner_text().strip()

    assert order_num_text == new_order_num_text, "[발주 규칙] 적용 제품 수 원복되지 않음"
    assert approve_num_text == new_approve_num_text, "[승인 규칙] 적용 제품 수 유지되지 않음"