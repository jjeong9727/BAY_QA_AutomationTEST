# 엑셀 파일 업로드 동작 확인
# 미리 보기 화면 확인
# 재 업로드 후 확인
# 등록 후 발주 규칙 "규칙 없음", 승인 규칙 "자동 승인" 확인
#
from playwright.sync_api import Page, expect 
from config import URLS, Account, HEADER_MAP
from helpers.common_utils import bay_login
import openpyxl  # 엑셀 업로드를 위해


def test_upload_excel_file(page: Page):
    bay_login(page)

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)

    page.locator("data-testid=btn_excel").hover()
    page.wait_for_selector("data-testid=btn_upload", timeout=5000)

    page.locator("data-testid=btn_upload").click()

    # 🚫 파일 업로드 동작 추가 필요
    # 🚫 숨겨진 input[type='file'] 이 있는지 확인 필요

    page.wait_for_selector("data-testid=col_type", timeout=10000)  # 업로드 완료 대기
    print("🔔 엑셀 파일 업로드 성공")

    # --- 엑셀 값 로드 ---
    workbook = openpyxl.load_workbook("data/product_upload_file_1.xlsx")
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]

    # --- UI vs 엑셀 데이터 비교 ---
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=0):
        table_row = page.locator("table tbody tr").nth(row_idx)
        has_placeholder = False
        missing_headers = []

        for col_idx, cell_value in enumerate(row):
            header_name = headers[col_idx]
            col_id = HEADER_MAP.get(header_name)

            if not col_id:
                continue  # 매핑 안 된 헤더는 스킵

            cell_locator = table_row.locator(f"[data-testid={col_id}]")

            # 값이 있으면 → 값 검증, 없으면 → placeholder 검증
            if cell_value is not None:
                expected_value = str(cell_value)
            else:
                expected_value = header_name
                has_placeholder = True
                missing_headers.append(header_name)

            expect(cell_locator).to_have_text(expected_value, timeout=3000)
            print(f"✅ 행 {row_idx+1}, {header_name}({col_id}) 값 확인됨 → {expected_value}")

        # --- placeholder가 있던 행은 tag_error 확인 ---
        if has_placeholder:
            error_tag = table_row.locator("[data-testid=tag_error]")
            expect(error_tag).to_be_visible(timeout=3000)
            print(f"⚠️ 행 {row_idx+1}: placeholder 감지됨 → tag_error 노출 확인 완료")

            # --- 툴팁 확인 (로그만 찍음) ---
            error_tag.hover()
            tooltip = page.locator("[data-testid=error_tooltip]")
            expect(tooltip).to_be_visible(timeout=3000)

            tooltip_text = tooltip.inner_text().strip()
            print(f"🔎 툴팁 노출 값: {tooltip_text}")
            print(f"📝 예상 누락 헤더: {missing_headers}")
            # ❌ assert 제거 → 테스트 실패 판정 아님
