from playwright.sync_api import Page, expect
from config import URLS, Account, HEADER_MAP, PRIORITY_ORDER
from helpers.common_utils import bay_login
from helpers.product_utils import upload_and_verify_excel
import openpyxl
import re
OPTIONAL_HEADERS = {"제품명(영문)", "제조사명(영문)"}
CATEGORY_MAP = {"의약품": "Medications", "보톡스": "botox", "메디톡스": "Medytox", "의료기기": "Medical Devices", "주사제": "Injection"}

def check_tooltip_order(tooltip: str, row_num: int):
    # 줄바꿈/마침표 단위 분리
    parts = [p.strip() for p in re.split(r"[.\n]", tooltip) if p.strip()]

    # PRIORITY_ORDER 키워드가 포함된 부분만 추출
    tooltip_order = []
    for p in parts:
        for key in PRIORITY_ORDER:
            if key in p and key not in tooltip_order:  # 중복 방지
                tooltip_order.append(key)

    # 실제 tooltip에서 감지된 키워드
    detected = [key for key in PRIORITY_ORDER if key in "".join(parts)]

    # 기대 순서는 detected (PRIORITY_ORDER에 맞춘 순서)
    expected_order = detected

    print(f"   📝 {row_num}행 Tooltip 검증")
    print(f"      - 원본 parts: {parts}")
    print(f"      - 추출된 오류 키워드 순서: {tooltip_order}")
    print(f"      - 기대 순서: {expected_order}")

    # 순서 비교
    assert tooltip_order == expected_order, (
        f"{row_num}행 Tooltip 순서 불일치\n"
        f"  실제: {tooltip_order}\n"
        f"  기대: {expected_order}"
    )

#  validation_1.xlsx 확인 [미입력 | [제품명+업체] 중복 | 업체 담당자 연락처 | 자동 발주 수량 0]
def test_upload_product_validation_first(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    file_path = "data/validation_1.xlsx"
    headers, row_count = upload_and_verify_excel(page, file_path)

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

    
    def get_tooltip_text(page, row_num: int) -> str:
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
    
    # --- 데이터 유효성 체크  ---
    for row_idx in range(row_count):
        table_row = page.locator("table tbody tr").nth(row_idx)
        ui_row_num = row_idx + 1
        row_data = {}
        total_rows += 1

        # ✅ zip(headers, row) 사용 → 헤더와 값 안전 매핑
        for header_name in headers:
            col_id = HEADER_MAP.get(header_name)
            if not col_id:
                continue

            cell_locator = table_row.locator(f"[data-testid={col_id}]")
            cell_value = cell_locator.text_content().strip() if cell_locator.count() > 0 else ""

            # --- 연락처 특별 처리 ---
            if header_name == "업체 담당자 연락처":
                contact_value = clean_excel_value(cell_value)
                digits_only = re.sub(r"\D", "", contact_value)

                # 1) 숫자 11자리 (010으로 시작 / 11자리 / 하이픈 OX)
                if digits_only and len(digits_only) == 11:
                    if digits_only.startswith("010"):
                        # ✅ 정상 포맷 (010으로 시작)
                        expected_contact = f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
                        expect(cell_locator).to_have_text(expected_contact, timeout=3000)
                        print(f"✅ {ui_row_num}행 연락처 정상 11자리 → 자동 포맷 확인: {expected_contact}")
                    else:
                        # ❌ 11자리지만 010으로 시작 안 함 → 오류 처리
                        expect(cell_locator).to_have_text(contact_value, timeout=3000)
                        print(f"⚠️ {ui_row_num}행 010으로 시작하지 않음 : {contact_value}")

                        error_tag = table_row.locator("[data-testid=tag_error]")
                        if error_tag.is_visible():
                            error_tag.hover()
                            tooltip_text = get_tooltip_text(page, ui_row_num)
                            if "번호여야 합니다" not in tooltip_text:
                                msg = f"{ui_row_num}행: 연락처 번호 규칙 오류 문구 누락"
                                errors.append(f"{msg} | 실제: {tooltip_text}")
                                summary.append(msg)

                # 2) 숫자가 11자리 미만 → 그대로 노출 + 오류 태그 + 툴팁 검증
                elif digits_only and len(digits_only) < 11:
                    expect(cell_locator).to_have_text(contact_value, timeout=3000)
                    print(f"⚠️ {ui_row_num}행 연락처 11자리 미만 확인: {contact_value}")

                    error_tag = table_row.locator("[data-testid=tag_error]")
                    if error_tag.is_visible():
                        error_tag.hover()
                        tooltip_text = get_tooltip_text(page, ui_row_num)
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
                tooltip_text = get_tooltip_text(page, ui_row_num)
                missing_headers = [
                    k for k, v in row_data.items()
                    if v == "" and k not in OPTIONAL_HEADERS  # ✅ 비필수 컬럼 제외
                ]
                for h in missing_headers:
                    if h not in tooltip_text:
                        msg = f"{ui_row_num}행: {h} 문구 누락"
                        errors.append(f"{msg} | 실제: {tooltip_text}")
                        summary.append(msg)

        # --- 중복 체크 (엑셀 + 서버) ---
        combo_key = (row_data.get("제품명"), row_data.get("업체명"))
        seen_combinations[combo_key] = seen_combinations.get(combo_key, 0) + 1
        if seen_combinations[combo_key] >= 2:
            excel_dup_candidates.add(combo_key)

        if combo_key in registered_products:
            error_tag = table_row.locator("[data-testid=tag_error]")
            if error_tag.is_visible():
                error_tag.hover()
                tooltip_text = get_tooltip_text(page, ui_row_num)
                if "이미 존재하는 제품명" not in tooltip_text:
                    msg = f"{ui_row_num}행: 서버 중복 문구 누락"
                    errors.append(msg); summary.append(msg)



        # --- 자동 발주 수량 0 ---
        if row_data.get("자동 발주 수량") == "0":
            auto_order_zero_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if error_tag.is_visible():
                error_tag.hover()
                page.wait_for_timeout(1000)
                tooltip_text = get_tooltip_text(page, ui_row_num)
                if "자동 발주 수량" not in tooltip_text:
                    msg = f"{ui_row_num}행: 자동 발주 수량 문구 누락"
                    errors.append(f"{msg} | 실제: {tooltip_text}")
                    summary.append(msg)
    # --- 루프 이후: 엑셀 중복 키 전체 검증 ---
    for dup_key in excel_dup_candidates:
        for row_idx in range(row_count):
            table_row = page.locator("table tbody tr").nth(row_idx)
            prd_name = table_row.locator("[data-testid=col_product]").text_content().strip()
            supplier = table_row.locator("[data-testid=col_supplier]").text_content().strip()

            if (prd_name, supplier) == dup_key:
                error_tag = table_row.locator("[data-testid=tag_error]")
                if error_tag.is_visible():
                    error_tag.hover()
                    tooltip_text = get_tooltip_text(page, row_idx + 1)
                    if "엑셀 파일에 중복된 제품명이" not in tooltip_text:
                        msg = f"{row_idx+1}행: 엑셀 내 중복 문구 누락"
                        errors.append(msg); summary.append(msg)

    # --- 결과 검증 ---
    if errors:
        print("❌ 검증 실패 상세 로그:")
        for e in errors:
            print("   -", e)
        assert False, f"{len(summary)}건의 검증 실패:\n" + "\n".join(summary)
    else:
        print("✅ 모든 검증 통과")


#  validation_2.xlsx 확인 [최대 값 입력 제한 | 영문 필드에 한글 | 숫자 필드에 문자]
def test_upload_product_validation_second(page: Page):
    bay_login(page, "admin")
    page.goto(URLS["bay_prdList"])

    file_path = "data/validation_2.xlsx"

    # --- 업로드 공통 유틸 ---
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1] if cell.value is not None]

    page.locator("data-testid=btn_excel").hover()
    page.locator("data-testid=btn_upload").click()
    page.set_input_files("input[type='file']", file_path)
    page.wait_for_selector("data-testid=col_type", timeout=10000)

    errors, summary = [], []
    total_rows = 0

    def clean_excel_value(cell_value):
        if cell_value is None:
            return ""
        if isinstance(cell_value, (int, float)):
            return f"{int(cell_value):,}"  # 천 단위 콤마 적용
            # return f"{int(cell_value)}"  # 콤마 없이 노출
        return str(cell_value).strip()

    def expect_cell_value(cell_locator, expected_value, timeout=3000):
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

    # --- 검증 시작 ---
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=0):
        if not any(row):
            continue
        table_row = page.locator("table tbody tr").nth(row_idx)
        ui_row_num = row_idx + 1
        total_rows += 1
        row_data = {}

        for header_name, cell_value in zip(headers, row):
            col_id = HEADER_MAP.get(header_name)
            if not col_id:
                continue

            cell_locator = table_row.locator(f"[data-testid={col_id}]")
            clean_value = clean_excel_value(cell_value)
            ui_expected = clean_value if clean_value != "" else header_name
            row_data[header_name] = clean_value
            expect_cell_value(cell_locator, ui_expected)

            # --- 제품명 / 제품명(영문) → 100자 제한 ---
            if header_name in ("제품명", "제품명(영문)") and len(clean_value) > 100:
                error_tag = table_row.locator("[data-testid=tag_error]")
                if error_tag.is_visible():
                    error_tag.hover()
                    tooltip = get_tooltip_text(ui_row_num)
                    if f"{header_name}" not in tooltip or "최대 100자까지 입력" not in tooltip:
                        msg = f"{ui_row_num}행 {header_name}: 100자 제한 오류"
                        errors.append(msg); summary.append(msg)

            # --- 업체명 → 30자 제한 ---
            if header_name == "업체명" and len(clean_value) > 30:
                error_tag = table_row.locator("[data-testid=tag_error]")
                if error_tag.is_visible():
                    error_tag.hover()
                    tooltip = get_tooltip_text(ui_row_num)
                    if "최대 30자까지 입력" not in tooltip:
                        msg = f"{ui_row_num}행 {header_name}: 30자 제한 오류"
                        errors.append(msg); summary.append(msg)

            # --- 업체 담당자명 → 15자 제한 ---
            if header_name == "업체 담당자명" and len(clean_value) > 15:
                error_tag = table_row.locator("[data-testid=tag_error]")
                if error_tag.is_visible():
                    error_tag.hover()
                    tooltip = get_tooltip_text(ui_row_num)
                    if "최대 15자까지 입력" not in tooltip:
                        msg = f"{ui_row_num}행 {header_name}: 15자 제한 오류"
                        errors.append(msg); summary.append(msg)

            # --- 단가(원) → 최대 99,999,999 ---
            if header_name == "단가(원)":
                digits = re.sub(r"\D", "", clean_value) or "0"
                if int(digits) > 99999999:
                    error_tag = table_row.locator("[data-testid=tag_error]")
                    if error_tag.is_visible():
                        error_tag.hover()
                        tooltip = get_tooltip_text(ui_row_num)
                        if "최대 입력 가능 금액" not in tooltip:
                            msg = f"{ui_row_num}행 단가 초과 오류"
                            errors.append(msg); summary.append(msg)

            # --- 안전 재고 / 자동 발주 수량 → 최대 9,999 ---
            if header_name in ("안전 재고", "자동 발주 수량"):
                digits = re.sub(r"\D", "", clean_value) or "0"
                if int(digits) > 9999:
                    error_tag = table_row.locator("[data-testid=tag_error]")
                    if error_tag.is_visible():
                        error_tag.hover()
                        tooltip = get_tooltip_text(ui_row_num)
                        if "최대 입력 가능 수량" not in tooltip:
                            msg = f"{ui_row_num}행 {header_name} 초과 오류"
                            errors.append(msg); summary.append(msg)

            # --- (영문) 컬럼에 한글 입력 ---
            if "(영문)" in header_name and re.search(r"[가-힣]", clean_value):
                error_tag = table_row.locator("[data-testid=tag_error]")
                if error_tag.is_visible():
                    error_tag.hover()
                    tooltip = get_tooltip_text(ui_row_num)
                    if "한글은 입력할 수 없는 항목" not in tooltip:
                        msg = f"{ui_row_num}행 {header_name}: 영문 전용 오류"
                        errors.append(msg); summary.append(msg)

            # --- 숫자 전용 컬럼에 문자열 입력 ---
            if header_name in ("단가(원)", "안전 재고", "자동 발주 수량"):
                if clean_value and not clean_value.isdigit():
                    error_tag = table_row.locator("[data-testid=tag_error]")
                    if error_tag.is_visible():
                        error_tag.hover()
                        tooltip = get_tooltip_text(ui_row_num)
                        if "숫자만 입력할 수 있습니다" not in tooltip:
                            msg = f"{ui_row_num}행 {header_name}: 숫자 전용 오류"
                            errors.append(msg); summary.append(msg)
            # --- 카테고리 한글-영문 매칭 검증 ---
            if header_name in ("구분명", "종류명", "제조사명"):
                # 대응되는 영문 헤더 찾기
                eng_header = header_name + "(영문)"
                kor_value = clean_value
                eng_value = row_data.get(eng_header, "")

                if kor_value and eng_value:
                    expected_eng = CATEGORY_MAP.get(kor_value)

                    if expected_eng:
                        if eng_value.lower() != expected_eng.lower():
                            error_tag = table_row.locator("[data-testid=tag_error]")
                            if error_tag.is_visible():
                                error_tag.hover()
                                tooltip = get_tooltip_text(ui_row_num)
                                if "등록된 카테고리의" not in tooltip:
                                    msg = f"{ui_row_num}행 {header_name}: 등록된 카테고리 매칭 불일치"
                                    errors.append(msg); summary.append(msg)
                    else:
                        error_tag = table_row.locator("[data-testid=tag_error]")
                        if error_tag.is_visible():
                            error_tag.hover()
                            tooltip = get_tooltip_text(ui_row_num)
                            if "생성되는 카테고리의" not in tooltip:
                                msg = f"{ui_row_num}행 {header_name}: 신규 카테고리 매칭 불일치"
                                errors.append(msg); summary.append(msg)


    # --- 최종 결과 ---
    if errors:
        print("❌ 유효성 검증 실패:")
        for e in errors:
            print("   -", e)
        assert False, f"{len(summary)}건 실패\n" + "\n".join(summary)
    else:
        print("✅ [최대 값 입력 제한 | 영문 입력 필드 | 숫자 입력 필드] 유효성 검증 통과")

#  validation_3.xlsx 확인 [성공 / 오류 필터 선택 후 개수 확인]
def test_upload_product_validation_third(page: Page):
    bay_login(page, "admin")
    page.goto(URLS["bay_prdList"])

    file_path = "data/validation_3.xlsx"
    headers, row_count = upload_and_verify_excel(page, file_path)

    rows = page.locator("table tbody tr")
    total_count = rows.count()
    error_rows = rows.filter(has=page.locator("[data-testid=tag_error]"))
    error_count = error_rows.count()
    success_count = total_count - error_count

    assert row_count == total_count, (f"❌ 엑셀({row_count})건과 UI({total_count})건 불일치")
    print(f"✅ 엑셀({row_count})건과 UI({total_count})건 일치")
    print(f"✅ 성공 행 수: {success_count}, ❌ 오류 행 수: {error_count}")

    # --- 1) 성공 필터 ---
    page.locator("data-testid=filter_success").click()
    expect(page.locator("table tbody tr")).to_have_count(success_count)
    print(f"🔍 성공 필터 → {success_count}개 확인")

    # --- 2) 성공+오류 (전체) ---
    page.locator("data-testid=filter_error").click()
    expect(page.locator("table tbody tr")).to_have_count(total_count)
    print(f"🔍 성공+오류 필터 → 전체 {total_count}개 확인")

    # --- 3) 오류만 ---
    page.locator("data-testid=filter_success").click()  # 해제 → 오류만
    expect(page.locator("table tbody tr")).to_have_count(error_count)
    print(f"🔍 오류 필터만 → {error_count}개 확인")

    # --- 4) 오류 필터 상태에서 툴팁 문구 + 순서 검증 (역순) ---
    filtered_rows = page.locator("table tbody tr")
    for i in reversed(range(filtered_rows.count())):
        row = filtered_rows.nth(i)
        error_tag = row.locator("[data-testid=tag_error]")

        if error_tag.is_visible():
            error_tag.hover()
            page.wait_for_timeout(1000)

            tooltip = page.locator(
                "[data-testid=error_tooltip][data-state='delayed-open']"
            ).text_content().strip()

            print(f"⚠️ {i+1}행 Tooltip → {tooltip}")
            check_tooltip_order(tooltip, i + 1)  # ✅ PRIORITY_ORDER 순서 검증

    # --- 5) 오류 필터 해제 (전체 복구) ---
    page.locator("data-testid=filter_error").click()
    expect(page.locator("table tbody tr")).to_have_count(total_count)
    print(f"🔍 필터 해제 후 전체 {total_count}개 확인")

    print("✅ 성공|오류 필터 및 툴팁 순서 검증 완료")

