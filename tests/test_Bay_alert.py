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

def test_check_alert(page:Page):
    bay_login(page)
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

    # [제품 관리] 엑셀 다운로드 확인
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

    # 제품 미선택 > 일괄 삭제 시도 
    page.locator("data-testid=btn_del_bulk").click()
    expect(page.locator("data-testid=toast_nodelete")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)

    # 재고 있는 제품 삭제 불가 확인
    page.locator("data-testid=input_search").fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    txt_delete = "제품을 삭제하시겠습니까?"
    for i in range(row_count):
        edit_button = rows.nth(i).locator("td:nth-child(12) >> text=삭제")
        if edit_button.is_visible():
            print(f"✅ {i}번째 행의 삭제 버튼 클릭")
            edit_button.click()
            page.wait_for_timeout(1000)
            expect(page.locator("data-testid=txt_delete")).to_be_visible(timeout=3000)
            page.locator("data-testid=btn_del").click()
            break
    
    expect(page.locator("data-testid=toast_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # [제품 관리] 이탈 팝업 확인
    # 등록화면
    page.goto(URLS["bay_prdList"])
    page.wait_for_timeout(2000)
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

    page.locator("data-testid=input_price").last.fill(100)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_search").fill("중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_rule_trigger", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_stk_safe").last.fill("5")
    page.wait_for_timeout(1000)
    # 자동 발주 수량 0 으로 선택 후 토스트 확인 
    page.locator("data-testid=input_stk_qty").last.fill("0")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_supplier_trigger").last.click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_supplier_search", "중복테스트")
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_supplier_item", has_text="중복테스트").click()
    page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_order_min")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 수정화면
    rows = page.locator("table tbody tr")
    row_count = rows.count()
    page.locator("data-testid=input_search").fill("발주 규칙 변경 제품")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    txt_toast = "자동 발주 수량은 최소 1개 이상이어야 합니다."
    rows.locator("td:nth-child(12) >> text=수정").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_stk_safe").fill("0")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_stk_qty").fill("0")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=toast_order_min")).to_have_text(txt_toast, timeout=3000)
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
    expect(page.locator("data-testid=drop_maker_trigger")).to_have_text("중복테스트", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

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
    page.wait_for_timeout(2000)

    # 이번달 확인
    page.click('[data-testid="btn_month"]')
    page.wait_for_timeout(2000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == month_start_str, f"❌ 시작일이 이번 달 1일이 아님 → {start_text}"
    assert end_text == today_str, f"❌ 종료일이 이번 달 말일이 아님 → {end_text}"
    page.wait_for_timeout(2000)

    # 오늘 날짜 확인
    page.locator("data-testid=btn_today").click()    
    page.wait_for_timeout(2000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == today_str, f"시작일 값이 오늘이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(2000)

    # 월별 버튼 확인    
    today = datetime.now()
    today_str = today.strftime("%Y. %m. %d")
    current_month = today.month
    active_month_buttons = []

    # 1~12월 버튼의 활성/비활성 상태 확인
    for month in range(1, 13):
        month_name = calendar.month_name[month].lower()  # 예: "january"
        btn = page.locator(f"data-testid=btn_{month_name}")
        is_disabled = btn.is_disabled()
        
        if month <= current_month:
            assert not is_disabled, f"❌ {month_name.capitalize()} 버튼은 활성화되어야 합니다."
            active_month_buttons.append(month_name)
        else:
            assert is_disabled, f"❌ 미래 월 {month_name.capitalize()} 버튼은 비활성화되어야 합니다."

    assert active_month_buttons, "❌ 활성화된 월 버튼이 없습니다."

    # 활성 월 버튼 클릭 → 시작일/종료일 확인
    for month_name in active_month_buttons:
        page.locator(f"data-testid=btn_{month_name}").click()
        page.wait_for_timeout(2000)
        
        start_text = page.locator('[data-testid="select_startday"] span').text_content()
        end_text = page.locator('[data-testid="select_endday"] span').text_content()
        
        assert start_text != today_str, f"❌시작일 삭제되지 않음 → {start_text}"
        assert end_text != today_str, f"❌종료일 삭제되지 않음 → {end_text}"

    # 다시 클릭해서 해제
    for month_name in active_month_buttons:
        page.locator(f"data-testid=btn_{month_name}").click()
        page.wait_for_timeout(1000)

    # 시작일/종료일 → 오늘 날짜 확인
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()

    assert start_text == today_str, f"❌시작일 오늘 아님 → {start_text}"
    assert end_text == today_str, f"❌종료일 오늘 아님 → {end_text}"
    print("✅ 날짜 범위 버튼 테스트 성공")
    page.wait_for_timeout(1000)

    
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


    # # [업체 전용 화면] 지난 발주 건 진입 불가 확인
    # order_id = "2"
    # accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
    # tracking_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
    # page.goto(accept_url)
    # expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    # page.fill("input[data-testid='input_name']", "권정의")
    # page.fill("input[data-testid='input_contact']", "01062754153")
    # page.locator("button[data-testid='btn_confirm']").last.click()
    # expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    # page.wait_for_timeout(1000)

    # page.goto(tracking_url)
    # expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    # page.fill("input[data-testid='input_name']", "권정의")
    # page.fill("input[data-testid='input_contact']", "01062754153")
    # page.locator("button[data-testid='btn_confirm']").last.click()
    # expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    # page.wait_for_timeout(1000)


    # [발주 규칙 관리] 중복명 확인
    rule_name = "중복테스트"
    memo = "중복값 확인"
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)

    page.locator("data-testid=btn_register").click()
    page.wait_for_timeout(2000)
    page.locator("data-testid=input_rule_name").fill(rule_name)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item", has_text="매주").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_weekday_trigger").click()
    page.wait_for_timeout(1000)
    for day in ["월요일", "수요일", "금요일"]:
        page.locator("data-testid=drop_weekday_item", has_text=day).click()
        page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_item",has_text="16").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_item", has_text="30").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_duplicate")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_cycle_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_cycle_item", has_text="매일").click()
    page.wait_for_timeout(1000)

    expect(page.locator("data-testid=drop_weekday_trigger")).not_to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_hour_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_hour_item",has_text="20").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_minute_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_minute_item", has_text="50").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_memo").fill(memo)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()

    expect(page.locator("data-testid=toast_duplicate")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    # [발주 내역] 
