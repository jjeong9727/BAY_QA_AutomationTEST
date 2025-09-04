from playwright.sync_api import Page, expect
from config import URLS, Account, HEADER_MAP
from helpers.common_utils import bay_login
import openpyxl
import re
OPTIONAL_HEADERS = {"제품명(영문)", "제조사명(영문)"}

def test_upload_product_validation(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)

    page.locator("data-testid=btn_excel").hover()
    page.wait_for_selector("data-testid=btn_upload", timeout=5000)

    # --- 엑셀 파일 업로드 ---
    page.set_input_files("input[type='file']", "data/validation.xlsx")
    print("📂 엑셀 파일 업로드 요청 완료")

    # --- 업로드 완료 대기 ---
    page.wait_for_selector("data-testid=col_type", timeout=10000)
    print("⬆️ 엑셀 파일 업로드 성공")
    expect(page.locator("data-testid=btn_save")).to_be_disabled(timeout=3000)

    # --- 엑셀 값 로드 ---
    workbook = openpyxl.load_workbook("data/validation.xlsx")
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1] if cell.value is not None]  # None 헤더 제거

    # --- 유틸 함수 ---
    def clean_excel_value(cell_value):
        if cell_value is None:
            return ""
        return str(cell_value).strip()

    def expect_cell_value(cell_locator, expected_value, timeout=3000):
        """input → value, span → text, 그 외 → td.textContent 로 비교"""
        input_locator = cell_locator.locator("input")
        span_locator = cell_locator.locator("span")

        if expected_value is None:
            expected_value = ""

        if input_locator.count() > 0:
            expect(input_locator).to_have_value(expected_value, timeout=timeout)
        elif span_locator.count() > 0:
            expect(span_locator).to_have_text(expected_value, timeout=timeout)
        else:
            expect(cell_locator).to_have_text(expected_value, timeout=timeout)

    def get_tooltip_text(row_num: int) -> str:
        tooltip = page.locator("[data-testid=error_tooltip][data-state='delayed-open']")
        page.wait_for_timeout(1000)
        raw_text = tooltip.text_content().strip()
        # 중복된 문구 제거
        parts = raw_text.split(")")
        deduped = []
        for p in parts:
            p = p.strip()
            if p and p + ")" not in deduped:
                deduped.append(p + ")")
        text = "".join(deduped)
        print(f"⚠️ {row_num}행 Tooltip 확인됨 → {text}")
        return text

    # --- 카운트/에러 변수 ---
    placeholder_count = 0
    duplicate_excel_count = 0
    duplicate_server_count = 0
    auto_order_zero_count = 0
    contact_length_error_count = 0
    total_rows = 0

    seen_combinations = {}
    excel_dup_candidates = set()
    both_dup_keys = set()
    registered_products = {("중복테스트", "중복테스트"), ("배치 확인 제품 1", "자동화업체D")}

    errors = []
    summary = []

    # --- 사전 검증: 엑셀 행 수 vs UI 행 수 ---
    excel_rows = sum(1 for row in sheet.iter_rows(min_row=2, values_only=True) if any(row))
    ui_rows = page.locator("table tbody tr").count()
    assert excel_rows == ui_rows, f"엑셀 {excel_rows}행 vs UI {ui_rows}행 불일치"

    # --- UI vs 엑셀 데이터 비교 ---
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=0):
        if not any(row):  # 전체가 None이면 스킵
            continue
        table_row = page.locator("table tbody tr").nth(row_idx)
        ui_row_num = row_idx + 1
        print(ui_row_num, row[0])
        row_data = {}
        total_rows += 1

        # ✅ zip(headers, row) 사용 → 헤더와 값 안전 매핑
        for header_name, cell_value in zip(headers, row):
            col_id = HEADER_MAP.get(header_name)
            if not col_id:
                continue

            cell_locator = table_row.locator(f"[data-testid={col_id}]")

            # --- 연락처 특별 처리 ---
            if header_name == "업체 담당자 연락처":
                contact_value = clean_excel_value(cell_value)
                digits_only = re.sub(r"\D", "", contact_value)

                # 1) 숫자 11자리 (하이픈 없음 → 프론트에서 자동 포맷팅)
                if digits_only and len(digits_only) == 11:
                    expected_contact = f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
                    expect(cell_locator).to_have_text(expected_contact, timeout=3000)
                    print(f"✅ {ui_row_num}행 연락처 11자리 → 자동 포맷 확인: {expected_contact}")

                # 2) 숫자가 11자리 미만 → 그대로 노출 + 오류 태그 + 툴팁 검증
                elif digits_only and len(digits_only) < 11:
                    expect(cell_locator).to_have_text(contact_value, timeout=3000)
                    print(f"⚠️ {ui_row_num}행 연락처 11자리 미만 확인: {contact_value}")

                    error_tag = table_row.locator("[data-testid=tag_error]")
                    if error_tag.is_visible():
                        error_tag.hover()
                        tooltip_text = get_tooltip_text(ui_row_num)
                        if "번호여야 합니다" not in tooltip_text:
                            msg = f"{ui_row_num}행: 연락처 길이 오류 문구 누락"
                            errors.append(f"{msg} | 실제: {tooltip_text}")
                            summary.append(msg)

                # 3) 숫자가 아예 없는 경우
                else:
                    if contact_value == "":
                        expect(cell_locator).to_have_text(header_name, timeout=3000)
                        print(f"ℹ️ {ui_row_num}행 연락처 빈칸 → 헤더명 표시 확인: {header_name}")
                    else:
                        expect(cell_locator).to_have_text(contact_value, timeout=3000)
                        print(f"ℹ️ {ui_row_num}행 연락처 숫자 없음 그대로 노출: {contact_value}")

                row_data[header_name] = contact_value
                continue

            # --- 연락처 외 항목 ---
            clean_value = clean_excel_value(cell_value)
            # print(f"{ui_row_num}행 {header_name} → raw:{cell_value!r}, clean:{clean_value!r}") # 전체 행의 값 확인 
            ui_expected = clean_value if clean_value != "" else header_name
            row_data[header_name] = clean_value

            expect_cell_value(cell_locator, ui_expected)

        print(f"📝 {ui_row_num}행 업로드 확인")

        # --- 미입력 에러 ---
        if "" in row_data.values():
            placeholder_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if not error_tag.is_visible():
                msg = f"{ui_row_num}행: 미입력 에러 태그 미노출"
                errors.append(msg)
                summary.append(msg)
            else:
                error_tag.hover()
                page.wait_for_timeout(1000)
                tooltip_text = get_tooltip_text(ui_row_num)
                missing_headers = [
                    k for k, v in row_data.items()
                    if v == "" and k not in OPTIONAL_HEADERS  # ✅ 비필수 컬럼 제외
                ]
                for h in missing_headers:
                    if h not in tooltip_text:
                        msg = f"{ui_row_num}행: {h} 문구 누락"
                        errors.append(f"{msg} | 실제: {tooltip_text}")
                        summary.append(msg)

        # --- 중복 체크 ---
        combo_key = (row_data.get("제품명"), row_data.get("업체명"))
        seen_combinations[combo_key] = seen_combinations.get(combo_key, 0) + 1
        server_dup = combo_key in registered_products
        if seen_combinations[combo_key] >= 2:
            excel_dup_candidates.add(combo_key)
        if server_dup:
            error_tag = table_row.locator("[data-testid=tag_error]")
            if error_tag.is_visible():
                error_tag.hover()
                page.wait_for_timeout(1000)
                tooltip_text = get_tooltip_text(ui_row_num)
                if "이미 존재하는" not in tooltip_text:
                    msg = f"{ui_row_num}행: 서버 중복 문구 누락"
                    errors.append(f"{msg} | 실제: {tooltip_text}")
                    summary.append(msg)

        if server_dup and combo_key in excel_dup_candidates:
            both_dup_keys.add(combo_key)

        # --- 자동 발주 수량 0 ---
        if row_data.get("자동 발주 수량") == "0":
            auto_order_zero_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if error_tag.is_visible():
                error_tag.hover()
                page.wait_for_timeout(1000)
                tooltip_text = get_tooltip_text(ui_row_num)
                if "자동 발주 수량" not in tooltip_text:
                    msg = f"{ui_row_num}행: 자동 발주 수량 문구 누락"
                    errors.append(f"{msg} | 실제: {tooltip_text}")
                    summary.append(msg)

    # --- 결과 검증 ---
    if errors:
        print("❌ 검증 실패 상세 로그:")
        for e in errors:
            print("   -", e)
        assert False, f"{len(summary)}건의 검증 실패:\n" + "\n".join(summary)
    else:
        print("✅ 모든 검증 통과")
