from playwright.sync_api import Page, expect
from config import URLS, Account, HEADER_MAP
from helpers.common_utils import bay_login
import openpyxl
import datetime

# 파일 다운로드 확인
def test_download_files(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)

    # --- 1. 제품목록 다운로드 ---
    with page.expect_download() as download_info:
        page.locator("data-testid=btn_excel").hover()
        page.wait_for_selector("data-testid=btn_download_file", timeout=3000)
        page.locator("data-testid=btn_download_file").click()
        page.wait_for_timeout(1000)

    download = download_info.value
    suggested_filename = download.suggested_filename

    today = datetime.date.today().strftime("%Y_%m_%d")
    expected_filename = f"{today}_제품목록.xlsx"

    assert suggested_filename == expected_filename, (
        f"❌ 파일명 불일치: 예상={expected_filename}, 실제={suggested_filename}"
    )
    print(f"✅ 제품목록 파일 다운로드 확인: {suggested_filename}")

    # --- 2. 템플릿 다운로드 ---
    with page.expect_download() as download_info:
        page.locator("data-testid=btn_excel").hover()
        page.wait_for_selector("data-testid=btn_download_template", timeout=3000)
        page.locator("data-testid=btn_download_template").click()
        page.wait_for_timeout(1000)

    download = download_info.value
    suggested_filename = download.suggested_filename
    expected_filename = "centurion_bay_제품등록_템플릿.xlsx"

    assert suggested_filename == expected_filename, (
        f"❌ 파일명 불일치: 예상={expected_filename}, 실제={suggested_filename}"
    )
    print(f"✅ 템플릿 파일 다운로드 확인: {suggested_filename}")

# 파일 업로드 유효성 검사
def test_upload_excel_file_validation(page: Page):
    empty = "data/empty_file.xlsx"
    image = "data/image_file.png"
    video = "data/video_file.mp4"
    template = "data/wrong_template.xlsx"

    bay_login(page, "admin")
    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)
    
    # 테스트 케이스 정의
    test_cases = [
        {"file": empty, "toast": "toast_empty", "msg": "업로드하신 파일에 정보가 없습니다."},
        {"file": template, "toast": "toast_template", "msg": "업로드하신 파일이 제공된 엑셀 템플릿과 형식이 다릅니다."},
        {"file": image, "toast": "toast_format", "msg": "지원하지 않는 파일 형식입니다."},
        {"file": video, "toast": "toast_format", "msg": "지원하지 않는 파일 형식입니다."},
    ]

    # 반복 실행 함수
    def upload_and_check(page: Page, file_path: str, toast_id: str, expected_msg: str):
        page.locator("data-testid=btn_excel").hover()
        page.wait_for_selector("data-testid=btn_upload", timeout=3000)
        page.locator("data-testid=btn_upload").click()
        page.wait_for_timeout(3000)
        # 파일 업로드
        page.set_input_files("input[type='file']", file_path)
        expect(page.locator(f"data-testid={toast_id}")).to_have_text(expected_msg, timeout=7000)
        print(f"✅ 파일 업로드 불가 확인: {file_path} → {expected_msg}")
        page.wait_for_timeout(2000)

    # 반복문으로 실행
    for case in test_cases:
        upload_and_check(page, case["file"], case["toast"], case["msg"])

# 파일 업로드 후 제품 유효성 검사
def test_upload_product_validation(page: Page):
    bay_login(page, "admin")

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_excel", timeout=5000)

    page.locator("data-testid=btn_excel").hover()
    page.wait_for_selector("data-testid=btn_upload", timeout=5000)
    page.locator("data-testid=btn_upload").click()

    # --- 엑셀 파일 업로드 ---
    page.set_input_files("input[type='file']", "data/product_empty_value.xlsx")
    print("📂 엑셀 파일 업로드 요청 완료")

    # --- 업로드 완료 대기 ---
    page.wait_for_selector("data-testid=col_type", timeout=10000)
    print("🔔 엑셀 파일 업로드 성공")

    # --- 엑셀 값 로드 ---
    workbook = openpyxl.load_workbook("data/product_empty_value.xlsx")
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]

    # --- 에러/성공 카운트 변수 ---
    placeholder_count = 0
    duplicate_excel_count = 0
    duplicate_server_count = 0
    seen_combinations = set()
    total_rows = 0

    # --- 서버에 이미 등록된 데이터 (fixture) ---
    registered_products = {
        ("테스트제품1", "공급업체A"),
        ("테스트제품2", "공급업체B"),
    }

    # --- UI vs 엑셀 데이터 비교 ---
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

        # --- placeholder 에러 체크 ---
        if "" in row_data.values():
            placeholder_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            expect(error_tag).to_be_visible(timeout=3000)
            print(f"⚠️ {row_idx+1}행: placeholder 에러 발생")

        # --- 중복 에러 체크 ---
        combo_key = (row_data.get("제품명"), row_data.get("업체명"))

        if combo_key in seen_combinations:
            duplicate_excel_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            expect(error_tag).to_be_visible(timeout=3000)
            print(f"⚠️ {row_idx+1}행: 엑셀 내 중복 에러 발생 → {combo_key}")

        elif combo_key in registered_products:
            duplicate_server_count += 1
            error_tag = table_row.locator("[data-testid=tag_error]")
            expect(error_tag).to_be_visible(timeout=3000)
            print(f"⚠️ {row_idx+1}행: 서버 등록 중복 에러 발생 → {combo_key}")

        else:
            seen_combinations.add(combo_key)

    # --- 합계 계산 ---
    total_errors = placeholder_count + duplicate_excel_count + duplicate_server_count
    success_count = total_rows - total_errors

    print(
        f"📝 미입력 에러: {placeholder_count}건, 엑셀 중복 에러: {duplicate_excel_count}건, 서버 중복 에러: {duplicate_server_count}건\n"
        f"📝 총 데이터 수: {total_rows}건, ✅성공: {success_count}건, ❌에러: {total_errors}건"
    )


    # --- UI 카운트 검증 ---
    ui_num_error = int(page.locator("[data-testid=num_error]").inner_text().strip().replace("건", ""))
    ui_num_success = int(page.locator("[data-testid=num_success]").inner_text().strip().replace("건", ""))

    assert ui_num_error == total_errors, f"❌ num_error 불일치: UI={ui_num_error}, 계산={total_errors}"
    assert ui_num_success == success_count, f"❌ num_success 불일치: UI={ui_num_success}, 계산={success_count}"
    assert total_rows == ui_num_error + ui_num_success, (
        f"❌ 총 행수 불일치: rows={total_rows}, error+success={ui_num_error+ui_num_success}"
    )

    print("✅ UI 카운트 검증 완료")
