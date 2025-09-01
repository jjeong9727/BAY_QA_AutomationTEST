# 엑셀 파일 업로드 동작 확인 (등록 성공만 확인)
# 미리 보기 화면 확인
# 등록 후 발주 규칙 "규칙 없음", 승인 규칙 "자동 승인" 확인
#
from playwright.sync_api import Page, expect 
from config import URLS, Account, HEADER_MAP
from helpers.common_utils import bay_login
from helpers.product_utils import append_product_name, verify_products_in_list
import openpyxl  # 엑셀 업로드를 위해

def test_upload_excel_file(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)
    page.locator("data-testid=btn_excel").hover()
    page.wait_for_selector("data-testid=btn_upload", timeout=5000)
    page.locator("data-testid=btn_upload").click()
    page.wait_for_timeout(3000)
    
    # --- 엑셀 업로드 ---
    page.set_input_files("input[type='file']", "data/success.xlsx")
    page.wait_for_selector("data-testid=col_type", timeout=10000)
    print("🔔 엑셀 파일 업로드 성공")

    # --- 엑셀 값 로드 ---
    workbook = openpyxl.load_workbook("data/success.xlsx")
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]

    product_list = []  # JSON 저장용 리스트
    total_rows = 0

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=0):
        table_row = page.locator("table tbody tr").nth(row_idx)
        row_data = {}
        total_rows += 1

        for col_idx, cell_value in enumerate(row):
            header_name = headers[col_idx]
            col_id = HEADER_MAP.get(header_name)
            if not col_id:
                continue

            cell_locator = table_row.locator(f"[data-testid={col_id}]")
            expected_value = str(cell_value) if cell_value is not None else ""
            expect(cell_locator).to_have_text(expected_value, timeout=3000)
            row_data[header_name] = expected_value

        # 원하는 값만 추출 → product_list에 저장
        product_info = {
            "prdname_kor": row_data.get("제품명", ""),
            "type_name": row_data.get("구분명", ""),
            "group": row_data.get("종류명", ""),
            "maker": row_data.get("제조사명", ""),
            "order_rule": "규칙 없음",
            "supplier": row_data.get("업체명", ""),
            "approve_rule": "자동 승인",
            "register": "excel",
            "safety": row_data.get("안전 재고"),
            "auto_order": row_data.get("자동 발주 수량"),
        }
        product_list.append(product_info)

    # --- UI 카운트 확인 ---
    expect(page.locator("[data-testid=num_error]")).to_have_text("0건", timeout=5000)
    expect(page.locator("[data-testid=num_success]")).to_have_text(f"{total_rows}건", timeout=5000)

    # --- 저장 버튼 클릭 ---
    page.locator("data-testid=btn_save").click()
    toast_text = f"{total_rows}개의 제품 등록이 완료되었습니다."
    expect(page.locator("data-testid=toast_register")).to_have_text(toast_text, timeout=7000)
    print(f"🎉 등록 완료 토스트 확인: {total_rows}건")

    # --- JSON 저장 (저장 버튼 성공 후) ---
    for product in product_list:
        append_product_name(**product)
    print(f"📝 업로드한 제품 JSON 저장 완료")
    verify_products_in_list(page, product_list, URLS["bay_prdList"], 3)
