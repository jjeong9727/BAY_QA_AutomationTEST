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

# [본사] 제품 수정 확인
def test_edit_products(page):
    edit_product = "수정 확인 제품"
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("[data-testid=\'btn_addprd\']", timeout=10000)

    page.locator("data-testid=input_search").fill(edit_product)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    product_value = first_row.locator("td:nth-child(3)").inner_text().strip()

    if product_value == "수정 확인 제품":
        new_name = "[수정] 수정 확인 제품"
    else:
        new_name = "수정 확인 제품"

    edit_button = first_row.locator("td:last-child >> text=수정")
    edit_button.click()
    page.wait_for_selector("[data-testid=\'input_prdname_kor\']", timeout=5000)

    page.locator("data-testid=input_prdname_kor").fill(new_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_edit")).to_have_text("제품을 수정하시겠습니까?", timeout=3000)
    expect(page.locator("data-testid=txt_subtitle")).to_have_text("확인 시, 해당 제품이 사용된 모든 영역이 변경됩니다.", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit")).to_have_text("제품 수정이 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill(new_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    product_value = first_row.locator("td:nth-child(3)").inner_text().strip()
    assert product_value == new_name, f"제품 수정한 값과 다르게 노출됨 기대값: {new_name}, 실제 값: {product_value}"

# [지점] 제품 확인 및 수정 (발주, 승인 규칙)  
def test_edit_approval_rule(page: Page):
    bay_login(page, "jekwon")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("[data-testid=\'btn_download\']", timeout=7000)
    
    # 발주 규칙 확인 (11열, json의 order_rule 사용)
    check_rule_for_products(page, all_products, col_index=11, expected_key="order_rule", label="발주 규칙")

    # 승인 규칙 확인 (12열, 기대 값은 항상 '자동 승인')
    check_rule_for_products(page, all_products, col_index=12, expected_key=None, label="승인 규칙")

    # 승인 규칙 수정 후 반영 확인
    edit_approval_rules_and_check(page, all_products)

# [지점] 제품 삭제
def test_delete_products(page:Page):
    bay_login(page, "jekwon")
    # 삭제 전 규칙 적용 제품 수 확인 (발주 규칙, 승인 규칙)
    global order_num_text, approve_num_text
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("[data-testid=\'btn_detail\']", timeout=10000)
    page.locator("data-testid=input_search").fill(order_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    order_num_cell = rows.nth(0).locator("td:nth-child(3)")
    order_num_text = order_num_cell.inner_text().strip()

    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("[data-testid=\'btn_register\']", timeout=10000)
    page.locator("data-testid=input_search").fill(approve_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
    approve_num_text = approve_num_cell.inner_text().strip()

    # ----- 개별 삭제 -----
    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("[data-testid=\'btn_download\']", timeout=5000)

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
        expect(page.locator("data-testid=txt_subtitle")).to_have_text("해당 제품이 삭제되며, 필요 시 복구할 수 있습니다.", timeout=3000)
        page.locator("data-testid=btn_del").click()
        expect(page.locator("data-testid=toast_delete")).to_have_text("제품 삭제가 완료되었습니다.", timeout=3000)
        page.wait_for_timeout(1000)

        # 삭제 버튼 > 복구 버튼으로 변경 및 버튼 활성화 확인 
        edit_button = first_row.locator("td:last-child >> button:has-text('수정')")
        restore_button = first_row.locator("td:last-child >> button:has-text('복구')")
        restore_text = restore_button.inner_text().strip()
        assert restore_text == "복구", f"복구 버튼으로 변경되지 않음 {restore_text}"
        expect(edit_button).to_be_enabled(timeout=3000)
        expect(restore_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)
        
    # -----일괄 삭제-----
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
    expect(page.locator("data-testid=txt_subtitle")).to_have_text("해당 제품이 삭제되며, 필요 시 복구할 수 있습니다.", timeout=3000)
    page.locator("data-testid=btn_del").click()
    expect(page.locator("data-testid=toast_delete_bulk")).to_have_text("3개의 제품 삭제가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    # 삭제 버튼 > 복구 버튼으로 변경 및 버튼 활성화 확인 
    for i in range(row_count):
        rows = page.locator("table tbody tr")
        target_row = rows.nth(i)
        edit_button = target_row.locator("td:last-child >> text=수정")
        restore_button = target_row.locator("td:last-child >> text=복구")
        expect(edit_button).to_be_visible(timeout=3000)
        expect(restore_button).to_be_visible(timeout=3000)
        page.wait_for_timeout(2000)
    
    # 재고관리 리스트 미노출 확인
    page.goto(URLS["bay_stock"])
    page.wait_for_selector("[data-testid=\'btn_stockadd\']", timeout=10000)

    page.locator("data-testid=input_search").fill(delete_products[0])
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    expect(page.locator("data-testid=txt_nosearch")).to_have_text("일치하는 항목이 없습니다", timeout=5000)
    
    # 재고 등록, 수동 발주 미노출 확인
    page.locator("data-testid=btn_order").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_trigger\']", timeout=5000)
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_search\']", timeout=3000)
    page.locator("data-testid=drop_prdname_search").fill(delete_products[1])
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=drop_prdname_item")).to_be_hidden(timeout=3000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_selector("[data-testid=\'btn_stockadd\']", timeout=5000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_trigger\']",timeout=5000)
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_search\']", timeout=3000)
    page.locator("data-testid=drop_prdname_search").fill(delete_products[2])
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=drop_prdname_item")).to_be_hidden(timeout=3000)

    # 적용 제품 수 확인 (발주 규칙: -1, 승인 규칙: 유지)
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("[data-testid=\'btn_detail\']", timeout=10000)
    page.locator("data-testid=input_search").fill(order_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_order_num_cell = rows.nth(0).locator("td:nth-child(3)")
    new_order_num_text = new_order_num_cell.inner_text().strip()

    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("[data-testid=\'btn_register\']", timeout=5000)
    page.locator("data-testid=input_search").fill(approve_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
    new_approve_num_text = new_approve_num_cell.inner_text().strip()


    assert order_num_text != new_order_num_text, "발주 규칙 적용 제품 수 변경 없음"
    assert approve_num_text == new_approve_num_text, "승인 규칙 적용 제품 수 유지되지 않음"
        
# [지점] 제품 복구
def test_restore_products(page:Page):
    bay_login(page, "jekwon")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("[data-testid=\'btn_download\']", timeout=10000)
    # -----개별 복구-----
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
        expect(page.locator("data-testid=subtitle")).to_have_text("확인 시, 제품이 복구되며 발주 및 재고 관리가 가능합니다.", timeout=3000)
        page.locator("data-testid=btn_confirm").click()
        expect(page.locator("data-testid=toast_restore")).to_have_text("제품 복구가 완료되었습니다.", timeout=3000)
        page.wait_for_timeout(1000)

        # 복구 버튼 > 삭제 버튼으로 변경 및 버튼 활성화 확인 
        edit_button = first_row.locator("td:last-child >> text=수정")
        delete_button = first_row.locator("td:last-child >> text=삭제")
        expect(edit_button).not_to_be_disabled(timeout=3000)
        expect(delete_button).not_to_be_disabled(timeout=3000)
        page.wait_for_timeout(1000)

    # -----일괄 복구------
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
    expect(page.locator("data-testid=subtitle")).to_have_text("확인 시, 제품이 복구되며 발주 및 재고 관리가 가능합니다.", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_restore")).to_have_text("3개의 제품 복구가 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    # 복구 버튼 > 삭제 버튼으로 변경 및 버튼 활성화 확인 
    for i in range(row_count):
        target_row = rows.nth(i)
        edit_button = target_row.locator("td:last-child >> text=수정")
        delete_button = target_row.locator("td:last-child >> text=삭제")

        expect(edit_button).to_be_enabled(timeout=3000)
        expect(delete_button).to_be_enabled(timeout=3000)
        page.wait_for_timeout(1000)

    # 재고관리 리스트 노출 확인
    page.goto(URLS["bay_stock"])
    page.wait_for_selector("[data-testid=\'btn_stockadd\']", timeout=3000)

    page.locator("data-testid=input_search").fill(delete_products[0])
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator('table tbody tr')
    product_cell = rows.nth(0).locator("td").nth(3)
    raw_text = product_cell.inner_text().strip()
    product_text = raw_text.partition("\n")[0]

    assert delete_products[0] == product_text, f"복구한 제품 재고관리에 미노출, 복구 제품: {delete_products[0]}"
    page.wait_for_timeout(1000)

    # 재고 등록, 수동 발주 노출 확인
    page.locator("data-testid=btn_order").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_trigger\']", timeout=5000)
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_search\']", timeout=3000)
    page.locator("data-testid=drop_prdname_search").fill(delete_products[1])
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=drop_prdname_item")).to_be_visible(timeout=3000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_selector("[data-testid=\'btn_stockadd\']", timeout=5000)
    page.locator("data-testid=btn_stockadd").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_trigger\']",timeout=5000)
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_selector("[data-testid=\'drop_prdname_search\']", timeout=3000)
    page.locator("data-testid=drop_prdname_search").fill(delete_products[2])
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=drop_prdname_item")).to_be_visible(timeout=3000)

        # 적용 제품 수 확인 (발주, 승인 규칙)
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("[data-testid=\'btn_detail\']", timeout=5000)
    page.locator("data-testid=input_search").fill(order_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_order_num_cell = rows.nth(0).locator("td:nth-child(3)")
    new_order_num_text = new_order_num_cell.inner_text().strip()

    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("[data-testid=\'btn_register\']", timeout=5000)
    page.locator("data-testid=input_search").fill(approve_rule)  
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    new_approve_num_cell = rows.nth(0).locator("td:nth-child(4)")
    new_approve_num_text = new_approve_num_cell.inner_text().strip()

    assert order_num_text == new_order_num_text, "[발주 규칙] 적용 제품 수 원복되지 않음"
    assert approve_num_text == new_approve_num_text, "[승인 규칙] 적용 제품 수 유지되지 않음"
