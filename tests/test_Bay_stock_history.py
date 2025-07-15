import random
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
    page.wait_for_timeout(300)
    page.locator(f'[data-testid="btn_day_{mmd}"]').click()
    page.wait_for_timeout(300)

    # 종료일 선택
    page.locator('[data-testid="select_endday"]').click()
    page.wait_for_timeout(300)
    page.locator(f'[data-testid="btn_day_{mmd}"]').click()
    page.wait_for_timeout(500)

    return ymd  # 화면에 표시되는 날짜 텍스트 검증용


def get_last_column_of_history2(page: Page) -> str:
    # 두 번째 history 내부의 테이블 → 첫 번째 행 → 첫번째 열
    row = page.locator('(//div[@data-testid="history"])[2]//table//tbody/tr').nth(0)
    first_col = row.locator('td').first
    return first_col.text_content().strip()

def get_have_stock_product(stock_manager, page):
    # 전체 상품 목록 가져오기
    all_products = stock_manager.load_product_from_json()

    # 조건에 맞는 상품 필터링
    filtered_products = [
        p for p in all_products
        if p.get("stock_qty", 0) >= 1 and p.get("order_flag", 1) != 0
    ]

    if not filtered_products:
        raise ValueError("조건에 맞는 상품이 없습니다.")

    # 랜덤으로 하나 선택
    product = random.choice(filtered_products)
    return product


def test_inflow_past(page):
    bay_login(page)
    stock_manager = StockManager(page)

    product = get_have_stock_product(stock_manager, page)
    product_name = product["kor"]
    current_stock = product["stock_qty"]
    yesterday_memo = "어제 날짜 입고 확인 테스트"
    day_before_memo = "그제 날짜 입고 확인 테스트"
    today_memo = "30자까지 제한인데요. 최대글자수 꽉꽉채워서 등록합니다"
    yesterday = datetime.today() - timedelta(days=1)
    day_before = datetime.today() - timedelta(days=2)
    today_str = "금일 재고 현황"
    yesterday_str = yesterday.strftime("%Y. %m. %d")
    day_before_str = day_before.strftime("%Y. %m. %d")
    
    
    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(2000)
    # 두 날짜에 대해 각각 등록
    register_stock_for_date(page, day_before, product_name, current_stock, day_before_memo)
    register_stock_for_date(page, yesterday, product_name, current_stock + 100, yesterday_memo)  # 이전 등록 반영

    # 재고 상세 진입 
    page.fill("data-testid=input_search", product_name)
    page.wait_for_timeout(500)
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

    # ✅ 2번째 history
    hist2_qty = int(get_table_cell_text(page, 2, 0, 2))
    hist2_memo = get_table_cell_text(page, 2, 0, 4)
    hist2_last = get_last_column_text(page, 2)

    assert hist2_qty == 200, f"[H2] 수량 불일치: {hist2_qty} != 200"
    assert hist2_memo == yesterday_memo, f"[H2] 메모 불일치: {hist2_memo} != {yesterday_memo}"
    assert hist2_last == hist3_last, f"[H2] 마지막 열 불일치: {hist2_last} != {hist3_last}"
    print(f"✅ H2 확인 완료")

    # ✅ 1번째 history
    expected_total = current_stock + 200
    hist1_qty = int(get_table_cell_text(page, 1, 0, 2))
    hist1_memo = get_table_cell_text(page, 1, 0, 4)
    hist1_last = get_last_column_text(page, 1)

    assert hist1_qty == expected_total, f"[H1] 수량 불일치: {hist1_qty} != {expected_total}"
    assert hist1_memo == today_memo, f"[H1] 메모 불일치: {hist1_memo} != {today_memo}"
    assert hist1_last == hist3_last, f"[H1] 마지막 열 불일치: {hist1_last} != {hist3_last}"
    print(f"✅ H1 확인 완료")

    