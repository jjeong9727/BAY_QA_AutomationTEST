from playwright.sync_api import Page, expect
import random
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.common_utils import bay_login
import calendar
from datetime import datetime, timedelta
import os

def format_date(date: datetime) -> str:
    return date.strftime("%Y. %m. %d")  # 띄어쓰기 포함

edit_name = "수정테스트"
txt_nosave = "변경 사항을 저장하지 않으시겠습니까?"

# 카테고리 관리
def test_alert_category(page:Page):
    bay_login(page, "admin")
        # [카테고리 관리] 이탈 팝업 확인
    page.goto(URLS["bay_category"])
    page.wait_for_timeout(2000)
    # 구분 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_category").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)
    # 종류 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_maker").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000) 
    # 제조사 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_type").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)
    # 구분 탭에서 이탈 취소 확인
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_category").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=input_kor").first).to_have_value(edit_name, timeout=3000)
    page.wait_for_timeout(1000)

# 제품 관리
def test_alert_product(page:Page):
    # [제품 관리] [지점]
    bay_login(page, "jekwon")
    # 엑셀 다운로드 확인
    # 오늘 날짜 포맷 (예: 2025_07_15)
    page.goto(URLS["bay_prdList"])
    today = datetime.now().strftime("%Y_%m_%d")
    with page.expect_download() as download_info:
        page.click('[data-testid="btn_download"]')
        page.wait_for_timeout(1000)
    download = download_info.value

    filename = download.suggested_filename
    print(f"📁 다운로드된 파일명: {filename}")
    assert filename.startswith(today), f"❌ 파일명이 오늘 날짜({today})로 시작하지 않습니다."

    # 필터 검색 확인 
    search_list = ["status", "type", "group", "maker", "name"]
    search_name = "중복테스트"
    col_map = {"type": 1, "group": 2, "name": 3, "maker": 4, "status": -1}
    status_options = ["사용 제품", "삭제 제품"]

    for search in search_list:
        num = col_map[search]
        if search == "status":
            for option in status_options:
                page.locator(f"data-testid=drop_{search}_trigger").click()
                page.wait_for_timeout(500)
                page.get_by_role("option", name=option, exact=True).click()
                page.wait_for_timeout(500)

                page.locator("data-testid=btn_search").click()
                page.wait_for_timeout(2000)
                rows= page.locator("table tbody tr")
                row_count = rows.count()
                expected_button = "삭제" if option == "사용 제품"  else "복구"

                for i in range(row_count):
                    delete_button = rows.nth(i).locator("td").nth(num).locator("button").nth(1).inner_text().strip() # 삭제 버튼 확인 
                    assert delete_button == expected_button, f"검색 결과 상이함. 검색 값: {expected_button}, 노출 값: {delete_button}" 
        elif search == "name":
            page.locator("data-testid=input_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows = page.locator("table tbody tr")
            first_row = rows.nth(0)
            raw_name_text = first_row.locator("td").nth(num).inner_text().strip()
            name_text = raw_name_text.partition("\n")[0]
            assert name_text == search_name, f"검색 결과 상이함 검색 값: {search_name}, 노출 값: {name_text}"
        else:
            page.locator(f"data-testid=drop_{search}_trigger").click()
            page.wait_for_selector(f"data-testid=drop_{search}_search", timeout=3000)
            page.locator(f"data-testid=drop_{search}_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator(f"data-testid=drop_{search}_item", has_text=search_name).click()
            page.wait_for_timeout(500)
            
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows= page.locator("table tbody tr")
            row_count = rows.count()
            num = col_map[search]
            for i in range(row_count):
                raw_kor_name = rows.nth(i).locator("td").nth(num).locator("div").nth(0).inner_text().strip() # 셀의 한글명만 
                kor_name = raw_kor_name.partition("\n")[0]
                assert kor_name == search_name, f"검색 결과 상이함. 검색 값: {search_name}, 노출 값: {kor_name}"
                page.wait_for_timeout(1000)  

        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)
    
    # 제품 미선택 > 선택 삭제 시도 
    page.locator("data-testid=btn_del_bulk").click()
    expect(page.locator("data-testid=toast_nodelete")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)

    # 재고 있는 제품 삭제 불가 확인
    page.locator("data-testid=input_search").fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    txt_delete = "제품을 삭제하시겠습니까?"
    for i in range(row_count):
        delete_button = rows.nth(i).locator("td:last-child >> text=삭제")
        if delete_button.is_visible():
            print(f"✅ {i+1}번째 행의 삭제 버튼 클릭")
            delete_button.click()
            page.wait_for_timeout(1000)
            expect(page.locator("data-testid=txt_delete")).to_have_text(txt_delete, timeout=3000)
            page.locator("data-testid=btn_del").click()
            expect(page.locator("data-testid=toast_stock")).to_be_visible(timeout=3000)
            break
    page.wait_for_timeout(1000)

    # 제품 미선택 > 선택 복구 시도
    page.locator("data-testid=btn_restore_bulk").click()
    expect(page.locator("data-testid=toast_select")).to_have_text("복구할 제품을 선택해주세요.", timeout=3000)
    page.wait_for_timeout(500)

    # 사용 상태의 제품 복구 불가 확인 
    page.locator("data-testid=input_search").fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    checkbox = first_row.locator("td").first
    checkbox.click()
    page.locator("data-testid=btn_restore_bulk").click()
    expect(page.locator("data-testid=toast_select")).to_have_text("복구할 제품을 선택해주세요.", timeout=3000)
    page.wait_for_timeout(500)    

    # [제품 관리] [본사]
    bay_login(page, "admin")
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)
    
    # 필터 검색 확인 
    search_list = ["type", "group", "maker", "name"]
    search_name = "중복테스트"
    col_map = {"type": 0, "group": 1, "name": 2, "maker": 3}

    for search in search_list:
        if search == "name":
            page.locator("data-testid=input_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows = page.locator("table tbody tr")
            first_row = rows.nth(0)
            raw_name_text = first_row.locator("td").nth(2).inner_text().strip()
            name_text = raw_name_text.partition("\n")[0]
            assert name_text == search_name, f"검색 결과 상이함 검색 값: {search_name}, 노출 값: {name_text}"
        else: 
            page.locator(f"data-testid=drop_{search}_trigger").click()
            page.wait_for_selector(f"data-testid=drop_{search}_search", timeout=3000)
            page.locator(f"data-testid=drop_{search}_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator(f"data-testid=drop_{search}_item", has_text=search_name).click()
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows= page.locator("table tbody tr")
            row_count = rows.count()
            num = col_map[search]

            for i in range(row_count):
                raw_kor_name = rows.nth(i).locator("td").nth(num).locator("div").nth(0).inner_text().strip() # 셀의 한글명만 
                kor_name = raw_kor_name.partition("\n")[0]
                assert kor_name == search_name, f"검색 결과 상이함. 검색 값:{search_name}, 노출 값: {kor_name}"
        
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)
    
    # 등록화면 이탈 팝업 확인
    page.locator("data-testid=btn_addprd").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_prdname_kor").fill(edit_name)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=input_prdname_kor").first).to_have_value(edit_name, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_type_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_type_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_group_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_group_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_group_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_maker_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_maker_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_price").last.fill("100")
    page.wait_for_timeout(1000)


    page.locator("data-testid=input_stk_safe").last.fill("5")
    page.wait_for_timeout(1000)
    # 자동 발주 수량 0 으로 선택 후 토스트 확인
    txt_toast = "자동 발주 수량은 최소 1개 이상이어야 합니다." 
    page.locator("data-testid=input_stk_qty").last.fill("0")
    page.wait_for_timeout(1000)
    # page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.locator("data-testid=btn_addrow").scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

        # 발주 규칙
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator('[data-testid="toast_order_min"]')).to_have_text(txt_toast, timeout=3000)
    page.wait_for_timeout(1000)

        # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 수정화면 이탈 팝업 확인
    page.locator("data-testid=input_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    rows.locator("td:last-child >> text=수정").first.click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_stk_safe").fill("0")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_stk_qty").fill("0")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    txt_edit = "제품을 수정하시겠습니까?"
    expect(page.locator("data-testid=txt_edit")).to_have_text(txt_edit, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout
    expect(page.locator('[data-testid="toast_order_min"]')).to_have_text(txt_toast, timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_maker_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_maker_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    page.wait_for_timeout(500)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # --- 제품 목록 다운로드 ---
    with page.expect_download() as download_info:
        page.locator("data-testid=btn_excel").hover()
        page.wait_for_selector("data-testid=btn_download_file", timeout=3000)
        page.locator("data-testid=btn_download_file").click()
        page.wait_for_timeout(1000)

    download = download_info.value
    suggested_filename = download.suggested_filename
    today = datetime.now().strftime("%Y_%m_%d")
    expected_filename = f"{today}_제품목록.xlsx"

    assert suggested_filename == expected_filename, (
        f"❌ 파일명 불일치: 예상={expected_filename}, 실제={suggested_filename}"
    )
    print(f"⬇️ 제품목록 파일 다운로드 확인: {suggested_filename}")

    # ---  템플릿 다운로드 ---
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
    print(f"⬇️ 템플릿 파일 다운로드 확인: {suggested_filename}")

    # --- 파일 업로드 유효성 검사 ---
    empty = "data/empty_file.xlsx"
    image = "data/image_file.png"
    txt = "data/text_file.txt"
    video = "data/video_file.mp4"
    template = "data/wrong_template.xlsx"
    

    test_cases = [
        {"file": empty, "toast": "toast_empty", "msg": "업로드하신 파일에 정보가 없습니다."},
        {"file": template, "toast": "toast_template", "msg": "업로드하신 파일이 제공된 엑셀 템플릿과 형식이 다릅니다."},
        {"file": txt, "toast": "toast_format", "msg": "지원하지 않는 파일 형식입니다."},
        {"file": image, "toast": "toast_format", "msg": "지원하지 않는 파일 형식입니다."},
        {"file": video, "toast": "toast_format", "msg": "지원하지 않는 파일 형식입니다."},
    ]

    def upload_and_check(page: Page, file_path: str, toast_id: str, expected_msg: str):
        page.locator("data-testid=btn_excel").hover()
        page.wait_for_selector("data-testid=btn_upload", timeout=3000)
        page.wait_for_timeout(3000)
        # 파일 업로드
        page.set_input_files("input[type='file']", file_path)
        expect(page.locator(f"data-testid={toast_id}")).to_have_text(expected_msg, timeout=7000)
        print(f"✅ 파일 업로드 불가 확인: {file_path} → {expected_msg}")
        page.wait_for_timeout(2000)

    # 반복문으로 실행
    for case in test_cases:
        upload_and_check(page, case["file"], case["toast"], case["msg"])

# 재고 관리
def test_alert_stock(page:Page):
    bay_login(page, "jekwon")
    # [재고관리] 이탈 팝업 확인
    # # 재고 등록화면
    txt_register = "해당 날짜로 재고 등록하시겠습니까?"
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_stockadd").click()
    expect(page.locator("data-testid=btn_addrow")).to_be_visible(timeout=3000)

    # 삭제 불가 Alert 확인	
    page.locator("data-testid=btn_addrow").click()
    page.wait_for_timeout(1000)
    close_btn = page.locator("button:has(svg path[id='Path 4'])").last
    expect(close_btn).to_be_visible()
    close_btn.click()
    page.wait_for_timeout(1000)   
    close_btn.click()
    expect(page.locator("data-testid=toast_nostock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 재고량 초과 알럿 확인
    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_status_item",has_text="입고").click()
    
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item",has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    stock_text = page.locator('[data-testid="txt_current_stock"]').inner_text().strip()
    try:
        current_stock = int(stock_text.replace(",", ""))
    except ValueError:
        raise ValueError(f"❌ 현재 재고 텍스트가 정수로 변환 불가: '{stock_text}'")
        # 재고보다 큰 수 계산 (예: +10)
    larger_qty = current_stock + 10
        # input_qty에 입력
    page.locator('[data-testid="input_qty"]').fill(str(larger_qty))
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_memo").fill("테스트 메모")
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator('[data-testid="toast_over_stock"]')).to_be_visible(timeout=7000)
    page.wait_for_timeout(1000)

    # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=input_memo")).to_have_value("테스트 메모", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_stockadd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 재고 리스트 날짜 퀵메뉴 확인
    today = datetime.today()
    week_ago = today - timedelta(days=7)
    today_str = format_date(today)
    week_ago_str = format_date(week_ago)
    start_of_month = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = today.replace(day=last_day)
    month_start_str = start_of_month.strftime("%Y. %m. %d")
    # 최근 1주 확인 
    page.click('[data-testid="btn_weekago"]')
    page.wait_for_timeout(1000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == week_ago_str, f"시작일 값이 일주일 전이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(1000)

    # 이번달 확인
    page.click('[data-testid="btn_month"]')
    page.wait_for_timeout(1000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == month_start_str, f"❌ 시작일이 이번 달 1일이 아님 → {start_text}"
    assert end_text == today_str, f"❌ 종료일이 이번 달 말일이 아님 → {end_text}"
    page.wait_for_timeout(1000)

    # 오늘 날짜 확인
    page.locator("data-testid=btn_today").click()    
    page.wait_for_timeout(1000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == today_str, f"시작일 값이 오늘이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(1000)

    # 월별 버튼 확인    
    today = datetime.now()
    today_str = today.strftime("%Y. %m. %d")
    current_month = today.month
    active_month_buttons = []

    # 1~12월 버튼의 활성/비활성 상태 확인
    for month in range(1, 13):
        btn = page.locator(f"[data-testid='btn_month_{month}']")
        is_disabled = btn.is_disabled()
        
        if month <= current_month:
            assert not is_disabled, f"❌ {month}월 버튼은 활성화되어야 합니다."
            active_month_buttons.append(month)
        else:
            assert is_disabled, f"❌ {month}월 버튼은 비활성화되어야 합니다."

    assert active_month_buttons, "❌ 활성화된 월 버튼이 없습니다."

    # 활성 월 버튼 클릭 → 시작일/종료일 확인
    for month_name in active_month_buttons:
        page.locator(f"data-testid=btn_month_{month_name}").click()
        page.wait_for_timeout(500)
        
        start_text = page.locator('[data-testid="select_startday"] span').text_content()
        end_text = page.locator('[data-testid="select_endday"] span').text_content()
        
        assert start_text != today_str, f"❌시작일 삭제되지 않음 → {start_text}"
        assert end_text != today_str, f"❌종료일 삭제되지 않음 → {end_text}"

    # 다시 클릭해서 해제
    for month_name in active_month_buttons:
        page.locator(f"data-testid=btn_month_{month_name}").click()
        page.wait_for_timeout(500)

    # 시작일/종료일 → 오늘 날짜 확인
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()

    assert start_text == today_str, f"❌시작일 오늘 아님 → {start_text}"
    assert end_text == today_str, f"❌종료일 오늘 아님 → {end_text}"
    print("✅ 날짜 범위 버튼 테스트 성공")
    page.wait_for_timeout(1000)

    # 필터 검색 확인 
    search_list = ["type", "group", "maker", "name"]
    search_name = "중복테스트"
    col_map = {"type": 1, "group": 2, "name": 3, "maker": 4}

    for search in search_list:
        num = col_map[search]
        if search == "name":
            page.locator("data-testid=input_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(3000)
            rows = page.locator("table tbody tr")
            first_row = rows.nth(0)
            raw_name_text = first_row.locator("td").nth(num).inner_text().strip()
            name_text = raw_name_text.partition("\n")[0]
            assert name_text == search_name, f"검색 결과 상이함 검색 값: {search_name}, 노출 값: {name_text}"
        else:    
            page.locator(f"data-testid=drop_{search}_trigger").click()
            page.wait_for_selector(f"data-testid=drop_{search}_search", timeout=3000)
            page.locator(f"data-testid=drop_{search}_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator(f"data-testid=drop_{search}_item", has_text=search_name).click()
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows= page.locator("table tbody tr")
            row_count = rows.count()

            for i in range(row_count):
                raw_kor_name = rows.nth(i).locator("td").nth(num).locator("div").nth(0).inner_text().strip() # 셀의 한글명만 
                kor_name = raw_kor_name.partition("\n")[0]
                assert kor_name == search_name, f"검색 결과 상이함. 검색 값:{search_name}, 노출 값: {kor_name}"
        
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)

    # 재고 리스트 일괄 수정 선택 알럿
    page.locator("data-testid=btn_edit_bulk").click()
    expect(page.locator("data-testid=toast_select_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
        # 재고 리스트 수정 알럿 
    page.locator("data-testid=btn_edit").first.click()
    row = page.locator("table tbody tr").first
    input_field = row.locator("td").nth(6).locator("input")
    input_field.scroll_into_view_if_needed()
    input_field.fill("100")
        # 수정중 알럿 확인 
    page.locator("data-testid=btn_reset").click()
    expect(page.locator("data-testid=toast_editing")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
        # 이탈 팝업 확인 
    page.locator("data-testid=btn_stockadd").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(input_field).to_have_value("100", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_stockadd").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

 # 발주 규칙 관리

# 발주 규칙 
def test_alert_order_rules(page:Page):
    bay_login(page, "admin")
    # [발주 규칙 관리] 중복명 확인
    rule_name = "중복테스트"
    memo = "중복값 확인"
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)

    page.locator("data-testid=btn_register").click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=7000)
    page.locator("data-testid=input_rule_name").fill(rule_name)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_1").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).not_to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_20").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_6").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_duplicate")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_2").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)
    dropdown_items = page.locator('div[data-testid="drop_weekday_item"] div[data-value]')
    count = dropdown_items.count()

    for i in range(count):
        text = dropdown_items.nth(i).inner_text().strip()
        if text in ["월요일", "수요일", "금요일"]:
            dropdown_items.nth(i).click()
            page.wait_for_timeout(1000)

    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_16").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_4").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_duplicate")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_cancel").click()
    page.wait_for_timeout(1000)

    # [발주 규칙 관리] 삭제 불가 확인
    page.locator("data-testid=input_search").fill(rule_name)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=btn_delete").click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("발주 규칙을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_using")).to_have_text("해당 발주 규칙은 사용 중입니다.", timeout=3000)

# 업체 전용 화면 
def test_alert_supplier_page(page:Page):
    bay_login(page, "jekwon")
    # [업체 전용 화면] 지난 발주 건 진입 불가 확인
    order_id_complete = "969"
    order_id_cancel = "966"

    accept_url = f"{URLS['base_accept_url']}/{order_id_complete}/accept"
    tracking_url = f"{URLS['base_accept_url']}/{order_id_cancel}/delivery"
    page.goto(accept_url)
    expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    page.fill("input[data-testid='input_name']", "권정의")
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.goto(tracking_url)
    expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    page.fill("input[data-testid='input_name']", "짱구")
    page.fill("input[data-testid='input_contact']", "01023032620")
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

# 승인 규칙 관리
def test_alert_approval_rules(page:Page):
    approver_1 = "권정의"
    bay_login(page, "jekwon")
    page.goto(URLS["bay_approval_rule"])
    page.wait_for_selector("data-testid=btn_register", timeout=7000)

    # 승인 규칙 등록 화면 중복값, 이탈 확인
    page.locator("data-testid=btn_register").click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=7000)

        # 승인자/참조자 삭제
    page.locator("data-testid=btn_delete_approver").click()
    expect(page.locator("data-testid=toast_noapprover")).to_have_text("최소 1명의 승인자를 등록해야 합니다.", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_delete_referrer").click()
    expect(page.locator("data-testid=drop_referrer_trigger")).to_be_hidden(timeout=3000)
    page.wait_for_timeout(1000)

        # 규칙명 중복 확인 
    page.locator("data-testid=input_rule_name").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_trigger").click()
    page.wait_for_selector("data-testid=drop_approver_search", timeout=3000)
    page.locator("data-testid=drop_approver_search").fill(approver_1)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_approver_item", has_text=approver_1).click()
    page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_duplicate")).to_have_text("이미 존재하는 승인 규칙명입니다.", timeout=3000)
    page.wait_for_timeout(1000)

        # 이탈 팝업 확인 
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=input_rule_name")).to_have_value("중복테스트", timeout=5000)
    
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=btn_register")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)

    # 승인 규칙 변경 제품 팝업 확인
    page.locator("data-testid=input_search").fill("수정테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    last_cell = first_row.locator("td").last # 1행 마지막 열 (수정 / 삭제 버튼)  
    name_cell = first_row.locator('td:nth-child(1)') # 1행 1열 (규칙명)
    name_text = name_cell.inner_text()
    
    if name_text == "수정테스트":
        edit_name = "[수정] 수정테스트"
    elif name_text == "[수정] 수정테스트":
        edit_name = "수정테스트"

    page.locator('[data-testid="btn_edit"]').first.click()
    page.wait_for_selector("data-testid=input_rule_name", timeout=5000)

    page.locator("data-testid=input_rule_name").fill(edit_name)
    page.wait_for_timeout(1000)

    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_title")).to_have_text("승인 규칙 변경 제품", timeout=3000)
    page.locator("data-testid=btn_cancel").last.click()
    expect(page.locator("data-testid=input_rule_name")).to_have_value(edit_name, timeout=5000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_title")).to_have_text("승인 규칙 변경 제품", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit_pending")).to_have_text("승인 규칙이 수정되었습니다. 다음 출고분부터 적용됩니다.", timeout=3000)
    # expect(page.locator("data-testid=toast_edit_pending")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 삭제 불가 확인
    page.locator("data-testid=input_search").fill(edit_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    last_cell = first_row.locator("td").last # 1행 마지막 열 (수정 / 삭제 버튼)  

    delete_button = last_cell.locator("data-testid=btn_delete")
    delete_button.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("승인 규칙을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=input_search")).to_have_value(edit_name, timeout=3000)
    delete_button.click()
    expect(page.locator("data-testid=txt_delete")).to_have_text("승인 규칙을 삭제하시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_using")).to_have_text("해당 승인 규칙은 사용 중입니다.", timeout=3000)
    page.wait_for_timeout(1000)

# 수동 발주 
def test_alert_manual_order(page:Page):
    txt_nodelete = "최소 1개 이상의 제품이 있어야 수동 발주가 가능합니다."
    txt_quantity = "수동 발주 수량은 최소 1개 이상이어야 합니다."
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    # 제품 개수 토스트 팝업 확인
    page.locator("data-testid=btn_order").click()
    page.wait_for_selector("data-testid=drop_prdname_trigger", timeout=3000)
    page.locator("data-testid=btn_delete").click()
    expect(page.locator("data-testid=toast_nodelete")).to_have_text(txt_nodelete, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_selector("data-testid=drop_prdname_search", timeout=3000)
    page.locator("data-testid=drop_prdname_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)
    # 수량 토스트 팝업 확인
    page.locator("data-testid=input_qty").fill("0")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_reject")).to_have_text("수동 발주를 진행하시겠습니까?", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_manual")).to_have_text(txt_quantity, timeout=3000)
    page.wait_for_timeout(1000)

    # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=input_qty")).to_have_value("0", timeout=3000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_order")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

# 발주 규칙 일괄 적용
def test_alert_order_rule_bulk(page:Page):
    bay_login(page, "admin")
    
    page.goto(URLS["bay_rules"])
    page.wait_for_selector("data-testid=btn_register_bulk", timeout=5000)
    
    page.locator("data-testid=btn_register_bulk").click()
    page.wait_for_selector("data-testid=drop_rule_trigger", timeout=5000)

    # 필터 검색 확인 
    search_list = ["type", "group", "maker", "name"]
    search_name = "중복테스트"
    col_map = {"type": 1, "group": 2, "name": 3, "maker": 4}

    for search in search_list:
        num = col_map[search]
        if search == "name":
            page.locator("data-testid=input_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(3000)
            rows = page.locator("table tbody tr")
            first_row = rows.nth(0)
            raw_name_text = first_row.locator("td").nth(num).inner_text().strip()
            name_text = raw_name_text.partition("\n")[0]
            assert name_text == search_name, f"검색 결과 상이함 검색 값: {search_name}, 노출 값: {name_text}"
        else:
            page.locator(f"data-testid=drop_{search}_trigger").click()
            page.wait_for_selector(f"data-testid=drop_{search}_search", timeout=3000)
            page.locator(f"data-testid=drop_{search}_search").fill(search_name)
            page.wait_for_timeout(500)
            page.locator(f"data-testid=drop_{search}_item", has_text=search_name).click()
            page.wait_for_timeout(500)
            
            page.locator("data-testid=btn_search").click()
            page.wait_for_timeout(2000)
            rows= page.locator("table tbody tr")
            row_count = rows.count()
            for i in range(row_count):
                raw_kor_name = rows.nth(i).locator("td").nth(num).locator("div").nth(0).inner_text().strip() # 셀의 한글명만 
                kor_name = raw_kor_name.partition("\n")[0]
                assert kor_name == search_name, f"검색 결과 상이함. 검색 값: {search_name}, 노출 값: {kor_name}"
                page.wait_for_timeout(1000)  

        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(2000)

    # 화면 이탈 확인 
    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_selector("data-testid=drop_rule_search", timeout=3000)
    page.locator("data-testid=drop_rule_search").fill(search_name)
    page.wait_for_timeout(500)
    page.locator(f"data-testid=drop_rule_item", has_text=search_name).click()
    page.wait_for_timeout(500)

    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    expect(page.locator("data-testid=subtitle")).to_have_text("이동 시, 수정한 내용이 저장되지 않습니다.", timeout=3000)
    page.locator("data-testid=btn_cancel").last.click()
    expect(page.locator("data-testid=drop_rule_trigger")).to_have_text(search_name, timeout=3000)
    page.wait_for_timeout(500)

    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=txt_nosave")).to_have_text("변경 사항을 저장하지 않으시겠습니까?", timeout=3000)
    expect(page.locator("data-testid=subtitle")).to_have_text("이동 시, 수정한 내용이 저장되지 않습니다.", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=btn_register")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
