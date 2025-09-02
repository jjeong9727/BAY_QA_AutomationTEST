from playwright.sync_api import Page, expect
from config import URLS, Account, HEADER_MAP
from helpers.common_utils import bay_login
import openpyxl
import datetime
import re

# 파일 업로드 후 제품 유효성 검사
def test_upload_product_validation(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)

    page.locator("data-testid=btn_excel").hover()
    page.wait_for_selector("data-testid=btn_upload", timeout=5000)
    page.locator("data-testid=btn_upload").click()

    # 엑셀 파일 업로드
    page.set_input_files("input[type='file']", "data/data/validation.xlsx")
    print("📂 엑셀 파일 업로드 요청 완료")

    # 업로드 완료 대기 
    page.wait_for_selector("data-testid=col_type", timeout=10000)
    print("⬆️ 엑셀 파일 업로드 성공")
    expect(page.locator("data-testid=btn_save")).to_be_disabled(timeout=3000)

    # 엑셀 값 로드 
    workbook = openpyxl.load_workbook("data/data/validation.xlsx")
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]

    # 에러/성공 카운트 변수 
    placeholder_count = 0
    duplicate_excel_count = 0
    duplicate_server_count = 0
    auto_order_zero_count = 0
    contact_length_error_count = 0
    total_rows = 0
    seen_combinations = set() # 엑셀 중복인 경우를 위한 세팅
    both_dup_keys = set() # 서버 중복 + 엑셀 중복인 경우를 위한 세팅 
    registered_products = {("중복테스트", "중복테스트"),("배치 확인 제품 1", "자동화업체D")} # 서버 중복인 경우를 위한 값
    errors = [] # Fail 건 수집용 (모든 에러 케이스 확인 후 최종 Fail 처리)

    # UI vs 엑셀 데이터 비교 
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=0):
        table_row = page.locator("table tbody tr").nth(row_idx)
        row_data = {}
        total_rows += 1

        for col_idx, cell_value in enumerate(row):
            header_name = headers[col_idx]
            col_id = HEADER_MAP.get(header_name)
            if not col_id:
                continue  # 매핑 안 된 헤더는 스킵

            cell_locator = table_row.locator(f"[data-testid={col_id}]")
            expected_value = str(cell_value) if cell_value is not None else header_name

            # UI 값과 비교
            expect(cell_locator).to_have_text(expected_value, timeout=3000)
            print(f"✅ {row_idx+1}행, {header_name}({col_id}) 값 확인됨 → {expected_value}")

            # dict 저장
            row_data[header_name] = str(cell_value) if cell_value is not None else ""

        # --- 미입력 에러 체크 ---
        if "" in row_data.values():
            placeholder_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if not error_tag.is_visible():
                errors.append(f"{row_idx+1}행: 미입력 에러 미노출")
            else:
                error_tag.hover()
                tooltip_text = page.locator("[data-testid=error_tooltip]").text_content().strip()
                # 실패 처리 하지 않고 모든 항목 확인 후 한번에 실패 처리
                if "필수 입력 항목" not in tooltip_text:
                    errors.append(f"🔔 {row_idx+1}행: 미입력 문구 불일치 | 실제 노출: {tooltip_text}")
                else :
                    print("✅ 미입력 유효성 문구 확인")

        # --- 중복 에러 체크 ---
        combo_key = (row_data.get("제품명"), row_data.get("업체명"))
        error_tag = table_row.locator("[data-testid=tag_error]")

        excel_dup = combo_key in seen_combinations
        server_dup = combo_key in registered_products

        if excel_dup or server_dup:
            if not error_tag.is_visible():
                errors.append(f"{row_idx+1}행: 중복 에러 태그 미노출")
            else:
                error_tag.hover()
                tooltip_text = page.locator("[data-testid=error_tooltip]").text_content().strip()
                lines = [t.strip() for t in tooltip_text.splitlines() if t.strip()]

                if excel_dup:
                    duplicate_excel_count += 1
                    if not any("엑셀 파일에 중복된" in t for t in lines):
                        errors.append(f"🔔 {row_idx+1}행: 엑셀 중복 문구 불일치 | 실제 노출: {lines}")
                    else:
                        print(f"✅ {row_idx+1}행: 엑셀 중복 유효성 문구 확인")

                if server_dup:
                    duplicate_server_count += 1
                    if not any("이미 존재하는" in t for t in lines):
                        errors.append(f"🔔 {row_idx+1}행: 서버 중복 문구 불일치 | 실제 노출: {lines}")
                    else:
                        print(f"✅ {row_idx+1}행: 서버 중복 유효성 문구 확인")

                # 서버 + 엑셀 중복 케이스라면 재검증 대상으로 추가
                if excel_dup and server_dup:
                    both_dup_keys.add(combo_key)

        # seen_combinations 는 무조건 업데이트
        seen_combinations.add(combo_key)

        # --- 서버+엑셀 중복 케이스 재검증 ---
        for dup_key in both_dup_keys:
            for j in range(total_rows):
                # j행의 제품/업체 조합 추출
                combo_j = (sheet.cell(j+2, headers.index("제품명")+1).value,
                        sheet.cell(j+2, headers.index("업체명")+1).value)
                if combo_j == dup_key:
                    row_j = page.locator("table tbody tr").nth(j)
                    error_tag = row_j.locator("[data-testid=tag_error]")
                    if not error_tag.is_visible():
                        errors.append(f"{j+1}행: 서버+엑셀 중복 태그 미노출")
                    else:
                        error_tag.hover()
                        tooltip_text = page.locator("[data-testid=error_tooltip]").text_content().strip()
                        if not ("엑셀 파일에 중복된" in tooltip_text and "이미 존재하는" in tooltip_text):
                            errors.append(f"🔔 {j+1}행: 서버+엑셀 중복 문구 불일치 | 실제 노출: {tooltip_text}")
                        else:
                            print(f"✅ {j+1}행: 서버+엑셀 중복 문구 모두 확인")

        # --- 자동 발주 수량 0 에러 체크 ---
        if row_data.get("자동 발주 수량") == "0":
            auto_order_zero_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if not error_tag.is_visible():
                # 실패 처리 하지 않고 모든 항목 확인 후 한번에 실패 처리
                errors.append(f"🔔 {row_idx+1}행: 자동 발주 수량 에러 미노출")
            else:
                error_tag.hover()
                tooltip_text = page.locator("[data-testid=error_tooltip]").text_content().strip()
                if "자동 발주 수량은 최소 1개" not in tooltip_text:
                    # 실패 처리 하지 않고 모든 항목 확인 후 한번에 실패 처리
                    errors.append(f"🔔 {row_idx+1}행: 자동 발주 수량 문구 불일치 | 실제: {tooltip_text}")
                else:
                    print("✅ 자동 발주 수량 유효성 문구 확인")

        # --- 연락처 길이 에러 체크 ---
        contact_value = row_data.get("연락처", "")
        digits_only = re.sub(r"\D", "", contact_value)
        if digits_only and len(digits_only) == 10:
            contact_length_error_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            if not error_tag.is_visible():
                # 실패 처리 하지 않고 모든 항목 확인 후 한번에 실패 처리
                errors.append(f"{row_idx+1}행: 연락처 10자리 태그 미노출")
            else:
                error_tag.hover()
                tooltip_text = page.locator("[data-testid=error_tooltip]").text_content().strip()
                if "11자리 번호여야" not in tooltip_text:
                    # 실패 처리 하지 않고 모든 항목 확인 후 한번에 실패 처리
                    errors.append(f"{row_idx+1}행: 연락처 문구 불일치 | 실제: {tooltip_text}")
                else:
                    print("✅ 연락처 유효성 문구 확인")

    # 모두 확인 후 실패 처리
    if errors:
        print("❌ 검증 실패 리스트:")
        for e in errors:
            print("   -", e)   # 콘솔에는 전체 메시지 (실제 노출 포함)

        # pytest 실패 메시지에는 "|" 이전 값만 사용
        trimmed = [e.split("|")[0].strip() for e in errors]
        assert False, f"{len(errors)}건의 검증 실패 발생:\n" + "\n".join(trimmed)
    else:
        print("✅ 모든 검증 통과")

    # --- 에러 합계 계산 ---
    total_errors = (
        placeholder_count 
        + duplicate_excel_count 
        + duplicate_server_count 
        + auto_order_zero_count
        + contact_length_error_count
    )
    success_count = total_rows - total_errors

    print(
        f"✔️ 미입력 에러: {placeholder_count}건\n"
        f"✔️ 엑셀 중복 에러: {duplicate_excel_count}건\n"
        f"✔️ 서버 중복 에러: {duplicate_server_count}건\n"
        f"✔️ 자동 발주 수량 에러: {auto_order_zero_count}건\n"
        f"✔️ 연락처 10자리 에러: {contact_length_error_count}건\n"
        f"📝 총 데이터 수: {total_rows}건, ✅성공: {success_count}건, ❌에러: {total_errors}건"
    )

    # 성공 에러 개수 카운트 확인 
    ui_num_error = int(page.locator("[data-testid=num_error]").inner_text().strip().replace("건", ""))
    ui_num_success = int(page.locator("[data-testid=num_success]").inner_text().strip().replace("건", ""))

    assert ui_num_error == total_errors, f"❌ num_error 불일치: UI={ui_num_error}, 계산={total_errors}"
    assert ui_num_success == success_count, f"❌ num_success 불일치: UI={ui_num_success}, 계산={success_count}"
    assert total_rows == ui_num_error + ui_num_success, (
        f"❌ 총 행수 불일치: rows={total_rows}, error+success={ui_num_error+ui_num_success}"
    )
    print("✅ UI 카운트 검증 완료")

    # 에러 필터 적용
    page.locator("data-testid=filter_error").click()
    page.wait_for_timeout(1000)
    error_rows = page.locator("table tbody tr").count()
    assert error_rows == total_errors, f"❌ 오류 건수 불일치: UI={error_rows}, 계산={total_errors}"
    print(f"✅ 오류 필터 확인 완료: {error_rows}건 (예상 {total_errors}건)")

    # 에러 + 성공 필터 적용 
    page.locator("data-testid=filter_success").click()  # 성공도 추가 선택
    page.wait_for_timeout(1000)
    rows_both = page.locator("table tbody tr").count()
    assert rows_both == total_rows, f"❌ 전체 건수 불일치: UI={rows_both}, 계산={total_rows}"
    print(f"✅ 에러+성공 동시 필터 확인 완료: {rows_both}건 (전체 {total_rows}건)")

    # 성공 필터 적용 
    page.locator("data-testid=filter_error").click()  # 에러만 해제 → 성공만 남음
    page.wait_for_timeout(1000)
    success_rows = page.locator("table tbody tr").count()
    assert success_rows == success_count, f"❌ 성공 건수 불일치: UI={success_rows}, 계산={success_count}"
    print(f"✅ 성공 필터 확인 완료: {success_rows}건 (예상 {success_count}건)")

    # 필터 초기화
    page.locator("data-testid=filter_success").click()  # 성공도 해제 → 전체 목록
    page.wait_for_timeout(1000)
    rows_reset = page.locator("table tbody tr").count()
    assert rows_reset == total_rows, f"❌ 필터 초기화 후 전체 건수 불일치: UI={rows_reset}, 계산={total_rows}"
    print(f"🔄 필터 초기화 완료: {rows_reset}건 (전체 {total_rows}건)")