import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.stock_utils import StockManager
from helpers.product_utils import update_product_flag, sync_product_names_with_server
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect

def get_filtered_products(stock_manager, page):
    # 서버와 동기화
    valid_products = sync_product_names_with_server(page)

    # 필터링
    return [
        p for p in valid_products
        if p.get("stock_qty", 0) <= p.get("safety_stock", 0)
        and p.get("order_flag", 1) == 0
    ]

def get_have_stock_product(stock_manager, page):
    # 전체 상품 목록 가져오기
    all_products = stock_manager.load_product_from_json()

    # 조건에 맞는 상품 필터링
    filtered_products = [
        p for p in all_products
        if p.get("stock_qty", 0) >= 1 and p.get("order_flag", 1) == 0
    ]

    if not filtered_products:
        raise ValueError("조건에 맞는 상품이 없습니다.")

    # 랜덤으로 하나 선택
    product = random.choice(filtered_products)
    return product

def test_stock_inflow(page):
    try:
        bay_login(page)
        

        stock_manager = StockManager(page)
        stock_manager.load_product_from_json()

        # 3개 제품을 랜덤으로 선택하여 입고 테스트 진행
        filtered_products = get_filtered_products(stock_manager, page)

        if len(filtered_products) < 3:
            print(f"❌ 조건에 맞는 제품이 {len(filtered_products)}개만 존재합니다. 3개 이상이 필요합니다.")
            return

        # 조건에 맞는 제품들 중에서 3개를 랜덤으로 선택
        selected_products = random.sample(filtered_products, 3)

        print("[선택된 제품]", [p["kor"] for p in selected_products])


        for product in selected_products:
            print(product)
            stock_manager.product_name = product['kor']  # 제품명을 클래스 속성에 저장
            stock_manager.search_product_by_name(product['kor'])

            inflow_qty = random.randint(6, 10)  # 랜덤 입고 수량
            stock_manager.perform_inflow(inflow_qty)  

            updated = stock_manager.get_current_stock()
            expected = stock_manager.initial_stock + inflow_qty
            assert updated == expected, f"[FAIL] {product['kor']} 입고 후 재고 오류: {expected} != {updated}"
            print(f"[PASS] 입고 확인: {product['kor']} → {updated}")

            # 입고 후 재고 값을 json 파일에 저장
            update_product_flag(product['kor'], stock_qty=expected)


    except Exception as e:
        print(f"❌ 입고 테스트 실패: {str(e)}")
        raise

def test_inflow_anotherday(page):
    bay_login(page)
    stock_manager = StockManager(page)

    product = get_have_stock_product(stock_manager, page)
    product_name = product["kor"]
    current_stock = product["stock_qty"]

    page.click("data-testid=btn_stockadd")
    page.wait_for_timeout(2000)
    # 과거 날짜 선택 
    yesterday = datetime.today() - timedelta(days=1)
    mmdd = yesterday.strftime("%m%d")  # MMDD 형식으로 변환
    txt_register = "해당 날짜로 재고 등록하시겠습니까?"
    page.locator("data-testid=select_date")
    page.wait_for_timeout(1000)
    yesterday = datetime.today() - timedelta(days=1)
    mmdd = yesterday.strftime("%m%d")  # MMDD 형식으로 변환
    today_str = yesterday.strftime("%y.%m.%d") # YYMMDD 형식으로 변환
    page.click(f"[data-testid=btn_day_{mmdd}]")
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_status_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_status_item", has_text="입고").click()
    page.wait_for_timeout(1000)

    page.locator("data-testid=drop_prdname_trigger").click()
    page.wait_for_timeout(1000)
    page.fill("data-testid=drop_prdname_search", product_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_prdname_item", has_text=product_name).click()
    expect(page.locator("data-testid=txt_current_stock")).to_have_text(current_stock, timeout=3000)
    instock = 100
    page.fill("data-testid=input_qty", instock)
    page.wait_for_timeout(500)
    expected = current_stock + instock
    page.fill("data-testid=input_memo", "과거 날짜 입고 확인 테스트")
    page.wait_for_timout(500)
    page.locator("data-testid=btn_save")
    expect(page.locator("data-testid=txt_register")).to_have_text(txt_register, timeout=3000)
    page.locator("data-testid=btn_confirm")
    expect(page.locator("data-testid=toast_stock")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 입고 후 재고 값을 json 파일에 저장
    update_product_flag(product['kor'], stock_qty=expected)

    page.fill("data-testid=input_search", product_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(1000)
    first_row_cell = page.locator("table tbody tr").first.locator("td").nth(3)
    cell_text = first_row_cell.inner_text().strip()
    assert cell_text == product_name, f"❌ 검색 결과가 일치하지 않음: {cell_text} != {product_name}"
    first_row_cell.click()  # 상세 페이지 진입
    date_locator = page.locator(f"text={today_str}")
    assert date_locator.is_visible(), f"❌ 화면 내에 날짜 {today_str} 이(가) 노출되지 않음"

















