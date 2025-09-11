import random
import json
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager, register_stock_for_date
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

def get_table_cell_text(page: Page, history_idx: int, row: int, col: int) -> str:
    """history_idx: 1, 2, 3 → 첫번째, 두번째, 세번째"""
    selector = f"(//div[@data-testid='history'])[{history_idx}]//table//tbody/tr[{row + 1}]/td[{col + 1}]"
    return page.locator(selector).text_content().strip()

def get_last_column_text(page: Page, history_idx: int) -> str:
    row = page.locator(f"(//div[@data-testid='history'])[{history_idx}]//table//tbody/tr").nth(0)
    return row.locator("td").last.text_content().strip()

def format_mmdd(date: datetime) -> str:
    return date.strftime("%m%d")

def format_ymd(date: datetime) -> str:
    return date.strftime("%Y. %m. %d")

def select_date_range(page: Page, date: datetime):
    mmd = format_mmdd(date)
    ymd = format_ymd(date)
    # 시작일 선택
    page.locator('[data-testid="select_startday"]').click()
    page.wait_for_timeout(1000)
    page.locator(f'[data-testid="btn_day_{mmd}"]').click()
    page.wait_for_timeout(1000)

    # 종료일 선택
    page.locator('[data-testid="select_endday"]').click()
    page.wait_for_timeout(1000)
    page.locator(f'[data-testid="btn_day_{mmd}"]').click()
    page.wait_for_timeout(1000)
    return ymd  # 화면에 표시되는 날짜 텍스트 검증용

def get_last_column_of_history2(page: Page) -> str:
    # 두 번째 history 내부의 테이블 → 첫 번째 행 → 첫번째 열
    row = page.locator('(//div[@data-testid="history"])[2]//table//tbody/tr').nth(0)
    first_col = row.locator('td').first
    return first_col.text_content().strip()
def get_manual_product():
    with open("product_name.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    # "register": "manual" 인 제품만 필터링
    manual_products = [p["kor"] for p in products if p.get("register") == "manual"]

    if not manual_products:
        raise ValueError("❌ 'register=manual' 제품을 찾을 수 없습니다.")

    # 랜덤으로 하나 선택
    return random.choice(manual_products)

today = datetime.today()
mmdd= today.strftime("%m%d")

# ✅ 지난 날짜 재고 수정 및 상세 확인 
def test_inflow_past(page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stock"])
    page.wait_for_selector("data-testid=btn_edit", timeout=10000)
    
    search_name = get_manual_product()

    page.locator("data-testid=input_search").fill(search_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)

    product_column = page.locator("table tbody tr").first.locator("td").nth(3)
    stock_column = page.locator("table tbody tr").first.locator("td").nth(5)
    stock_text = stock_column.text_content().strip()
    raw_product = product_column.locator("div").first.text_content().strip()
    product_name = raw_product.splitlines()[0].strip()
    current_stock = int(stock_text)
    print(f"재고량 : {stock_text}, 제품명 : {product_name}")
    yesterday_memo = "어제 날짜 입고 확인 테스트"
    day_before_memo = "그제 날짜 입고 확인 테스트"
    today_memo = "30자까지 제한인데요. 최대글자수 꽉꽉채워서 등록합니다"
    yesterday = datetime.today() - timedelta(days=1)
    day_before = datetime.today() - timedelta(days=2)
    today_str = "금일 재고 현황"
    yesterday_str = yesterday.strftime("%Y. %m. %d")
    day_before_str = day_before.strftime("%Y. %m. %d")
    
    page.wait_for_timeout(2000)
    # 두 날짜에 대해 각각 등록
    register_stock_for_date(page, yesterday, search_name, current_stock, yesterday_memo)  
    register_stock_for_date(page, day_before, search_name, current_stock+100, day_before_memo)

    # 재고 상세 진입 
    page.fill("data-testid=input_search", product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    first_row_cell = page.locator("table tbody tr").first.locator("td").nth(3)
    cell_text = first_row_cell.inner_text().strip().split("\n")[0]
    assert cell_text == product_name, f"❌ 검색 결과가 일치하지 않음: {cell_text} != {product_name}"
    first_row_cell = page.locator("table tbody tr").first.locator("td").nth(3)
    first_row_cell.locator("div").first.click()
    expect(page.locator("data-testid=btn_back")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=btn_stockadd")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    first_row_cell.locator("div").first.click()
    expect(page.locator("data-testid=txt_today")).to_have_text(today_str, timeout=3000)
    page.wait_for_timeout(500)

    # 날짜 및 상태 필터
    day1_str = select_date_range(page, day_before)

    # 문구 확인
    expect(page.locator('[data-testid="txt_today"]')).to_be_visible()
    expect(page.locator('[data-testid="txt_date"]')).to_have_text(day1_str)

    # 값 추출
    value_day1 = get_last_column_of_history2(page)
    print(f"[📅 그제] history2의 상태 값: {value_day1}")

    # ✅ 어제 날짜 기준 테스트
    day2_str = select_date_range(page, yesterday)

    # 문구 확인
    expect(page.locator('[data-testid="txt_today"]')).to_be_visible()
    expect(page.locator('[data-testid="txt_date"]')).to_have_text(day2_str)

    # 값 추출
    value_day2 = get_last_column_of_history2(page)
    print(f"[📅 어제] history2의 상태 값: {value_day2}")

    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(1000)

    # 텍스트 문구 확인
    expect(page.locator('[data-testid="txt_today"]')).to_have_text(today_str)
    txt_dates = page.locator('[data-testid="txt_date"]')
    expect(txt_dates.nth(0)).to_have_text(yesterday_str)
    expect(txt_dates.nth(1)).to_have_text(day_before_str)

    # ✅ 3번째 history
    hist3_qty = int(get_table_cell_text(page, 3, 0, 2))  # 3번째 열 = index 2
    hist3_memo = get_table_cell_text(page, 3, 0, 4)      # 5번째 열 = index 4
    hist3_last = get_last_column_text(page, 3)

    assert hist3_qty == 100, f"[H3] 수량 불일치: {hist3_qty} != 100"
    assert hist3_memo == day_before_memo, f"[H3] 메모 불일치: {hist3_memo} != {day_before_memo}"
    print(f"✅ H3 확인 완료")

    # 2번째 history
    hist2_qty = int(get_table_cell_text(page, 2, 0, 2))
    hist2_memo = get_table_cell_text(page, 2, 0, 4)
    hist2_last = get_last_column_text(page, 2)

    assert hist2_qty == 200, f"[H2] 수량 불일치: {hist2_qty} != 200"
    assert hist2_memo == yesterday_memo, f"[H2] 메모 불일치: {hist2_memo} != {yesterday_memo}"
    assert hist2_last == hist3_last, f"[H2] 마지막 열 불일치: {hist2_last} != {hist3_last}"
    print(f"✅ H2 확인 완료")

    # 1번째 history
    expected_total = current_stock + 200
    hist1_qty = int(get_table_cell_text(page, 1, 0, 2))
    hist1_memo = get_table_cell_text(page, 1, 0, 4)
    hist1_last = get_last_column_text(page, 1)

    assert hist1_qty == expected_total, f"[H1] 수량 불일치: {hist1_qty} != {expected_total}"
    acceptable_memos = [
        today_memo,
        "2개의 메모가 있습니다.",
        "-"
    ]
    assert hist1_memo in acceptable_memos, f"[H1] 메모 불일치: {hist1_memo} != {today_memo}"
    assert hist1_last == hist3_last, f"[H1] 마지막 열 불일치: {hist1_last} != {hist3_last}"
    print(f"✅ H1 확인 완료")

    update_product_flag(name_kor=product_name, stock_qty=expected_total)

# ✅ 재고 일괄 수정 및 상세 확인 
def test_stock_bulk_edit(page:Page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    inflow_data = 25
    new_inflow_data = 15
    txt_bulk = "2개의 재고 입고가 완료되었습니다."
    txt_edit = "재고 입고가 완료되었습니다."

    search_name = f"엑셀업로드_{mmdd}"
    page.locator("data-testid=input_search").fill(search_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    
    row1 = page.locator("table tbody tr").first
    row2 = page.locator("table tbody tr").nth(1)
    checkbox1 = row1.locator("td").first
    checkbox2 = row2.locator("td").first
    product_column1 = row1.locator("td").nth(3)
    product_column2 = row2.locator("td").nth(3)
    stock_column1 = row1.locator("td").nth(5)
    stock_column2 = row2.locator("td").nth(5)
    stock_text1 = stock_column1.text_content().strip()
    stock_text2 = stock_column2.text_content().strip()
    product_name1 = product_column1.locator("div").first.text_content().strip()
    product_name2 = product_column2.locator("div").first.text_content().strip()

    # 재고 2개 일괄 수정(2개 모두) 후 상세 내역(2개 모두) 확인 
    page.locator("data-testid=btn_edit_bulk").click()
    expect(page.locator("data-testid=toast_select_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    legacy1 = row1.locator("td").nth(6).locator("div")
    inflow_legacy1 = legacy1.text_content().strip()
    legacy2 = row2.locator("td").nth(6).locator("div")
    inflow_legacy2 = legacy2.text_content().strip()
    checkbox1.click()
    checkbox2.click()
    page.locator("data-testid=btn_edit_bulk").click()
    page.wait_for_timeout(1000)
    print(f"첫번째 항목 기존 입고량 : {inflow_legacy1}, 두번째 항목 기존 입고량: {inflow_legacy2}")
    input_field1 = row1.locator("td").nth(6).locator("input")
    input_field2 = row2.locator("td").nth(6).locator("input")

    inflow_1 = int(inflow_data)+int(inflow_legacy1)
    inflow_2 = int(inflow_data)+int(inflow_legacy2)
    input_field1.fill(str(inflow_1))
    page.wait_for_timeout(500)
    input_field2.fill(str(inflow_2))
    page.wait_for_timeout(500)  
    change1 = datetime.now()
    page.locator("data-testid=btn_edit_bulk").click()
    expect(page.locator("data-testid=toast_inflow")).to_have_text(txt_bulk, timeout=7000)
    page.wait_for_timeout(1000)
    
    # 첫번째 재고 상세 진입
    first_history = row1.locator("td").nth(3)
    first_history.locator("div").first.click()
    page.wait_for_timeout(1000)
    change_history1 = change1.strftime("%Y. %m. %d %H:%M")
    history1 = get_last_column_text(page, 1)
    actual_history1 = history1.split(',')[0].strip()
    assert change_history1 == actual_history1, f"변경 이력 불일치: {change_history1} != {actual_history1}"
    page.wait_for_timeout(1000)
    inflow1 = int(get_table_cell_text(page, 1, 0, 3)) # 입출고 수량
    assert inflow1 == inflow_1, f"입고량 불일치 : {inflow1} != {inflow_1}"
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_timeout(1000)
    # 두번째 재고 상세 진입
    second_history = row2.locator("td").nth(3)
    second_history.locator("div").first.click()
    page.wait_for_timeout(1000)
    history2 = get_last_column_text(page, 1)
    actual_history2 = history2.split(',')[0].strip()
    assert change_history1 == actual_history2, f"변경 이력 불일치: {change_history1} != {actual_history2}"
    page.wait_for_timeout(1000)
    inflow2 = int(get_table_cell_text(page, 1, 0, 3)) # 입출고 수량
    assert inflow2 == inflow_2, f"입고량 불일치 : {inflow2} != {inflow_2}"
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_timeout(1000)

    # 재고 2개 일괄 수정(1개만 수정) 후 상세 내역(2개 모두) 확인
    page.locator("data-testid=btn_edit_bulk").click()
    expect(page.locator("data-testid=toast_select_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    checkbox1.click()
    checkbox2.click()
    page.locator("data-testid=btn_edit_bulk").click()
    page.wait_for_timeout(1000)

    input_field1 = row1.locator("td").nth(6).locator("input")

    input_field1.fill(str(new_inflow_data))
    page.wait_for_timeout(500)
    change2 = datetime.now()
    page.locator("data-testid=btn_edit_bulk").click()
    expect(page.locator("data-testid=toast_inflow")).to_have_text(txt_edit, timeout=3000)
    page.wait_for_timeout(1000)

    # 첫번째 재고 상세 진입
    first_history = row1.locator("td").nth(3)
    first_history.locator("div").first.click()
    page.wait_for_timeout(1000)
    change_history2 = change2.strftime("%Y. %m. %d %H:%M")
    history1 = get_last_column_text(page, 1)
    actual_history1 = history1.split(',')[0].strip()
    assert change_history2 == actual_history1, f"변경 이력 불일치: {change_history2} != {actual_history1}"
    page.wait_for_timeout(1000)
    inflow1 = int(get_table_cell_text(page, 1, 0, 3)) # 입출고 수량
    assert inflow1 == new_inflow_data, f"입고량 불일치 : {inflow1} != {new_inflow_data}"
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_timeout(1000)
    # 두번째 재고 상세 진입
    second_history = row2.locator("td").nth(3)
    second_history.locator("div").first.click()
    page.wait_for_timeout(1000)
    history2 = get_last_column_text(page, 1)
    actual_history2 = history2.split(',')[0].strip()
    # 두번째 수정 하지 않아 첫번째 수정 시간과 노출되는 시간 비교
    assert change_history1 == actual_history2, f"변경 이력 불일치: {change_history1} != {actual_history2}" 
    page.wait_for_timeout(1000)
    inflow2 = int(get_table_cell_text(page, 1, 0, 3)) # 입출고 수량
    # 두번째 수정 하지 않아 첫번째 입고량과 노출되는 값 비교
    assert inflow2 == inflow_2, f"입고량 불일치 : {inflow2} != {inflow_2}"
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    page.wait_for_timeout(1000)

    update_product_flag(name_kor=product_name1, stock_qty=int(stock_text1)+int(new_inflow_data))
    update_product_flag(name_kor=product_name2, stock_qty=int(stock_text2)+int(inflow_2))
