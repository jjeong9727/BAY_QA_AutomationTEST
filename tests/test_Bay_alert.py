from playwright.sync_api import Page, expect
import random
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.common_utils import bay_login

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
        edit_button = rows.nth(i).locator("td:nth-child(11) >> text=삭제")
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
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_addprd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 수정화면
    rows = page.locator("table tbody tr")
    row_count = rows.count()

    for i in range(row_count):
        edit_button = rows.nth(i).locator("td:nth-child(11) >> text=수정")
        if edit_button.is_visible():
            print(f"✅ {i}번째 행의 수정 버튼 클릭")
            edit_button.click()
            break
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
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_save").click()
    expect(page.locator('[data-testid="toast_over_stock"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)


    # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_have_text(txt_nosave, timeout=3000)
    page.wait_for_timeout(500)
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
    month_ago = today - timedelta(days=30)
    today_str = format_date(today)
    week_ago_str = format_date(week_ago)
    month_ago_str = format_date(month_ago)

    # 최근 1주 확인 
    page.click('[data-testid="btn_weekago"]')
    page.wait_for_timeout(1000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == week_ago_str, f"시작일 값이 일주일 전이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(2000)

    # 최근 1개월 확인
    page.click('[data-testid="btn_monthago"]')
    page.wait_for_timeout(2000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == month_ago_str, f"시작일 값이 한 달 전이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(2000)

    # 오늘 날짜 확인
    page.locator("data-testid=btn_today").click()    
    page.wait_for_timeout(2000)
    start_text = page.locator('[data-testid="select_startday"] span').text_content()
    end_text = page.locator('[data-testid="select_endday"] span').text_content()
    assert start_text == today_str, f"시작일 값이 오늘이 아님 → {start_text}"
    assert end_text == today_str, f"종료일 값이 오늘이 아님 → {end_text}"
    page.wait_for_timeout(2000)

    print("✅ 날짜 범위 버튼 테스트 성공")
    
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


    # [업체 전용 화면] 지난 발주 건 진입 불가 확인
    order_id = "2"
    accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
    tracking_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
    page.goto(accept_url)
    expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    page.fill("input[data-testid='input_name']", "권정의")
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.goto(tracking_url)
    expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
    page.fill("input[data-testid='input_name']", "권정의")
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=toast_expired")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    

    
    


