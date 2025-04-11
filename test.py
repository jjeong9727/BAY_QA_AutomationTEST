from playwright.sync_api import sync_playwright
# from helpers.order_status_utils import get_order_id_from_order_list
from config import URLS, Account

def get_order_id_from_order_list(page, product_name):
    # 제품명을 기준으로 해당 <td>를 찾음
    print("제품 찾는 중...")
    first_table = page.locator("table").first  # 첫 번째 테이블만 선택
    rows = first_table.locator("tbody tr").all()  # 첫 번째 테이블의 모든 행을 가져옴

    for row in rows:
        # 해당 행에서 제품명이 일치하는지 확인
        row_product_name = row.locator("td").nth(1).locator("p").inner_text().strip()  # p 태그의 텍스트를 추출
        print(f"검색된 제품명: {row_product_name}")

        # 제품명이 일치하는지 비교
        if row_product_name == product_name:
            # 제품명이 일치하면 해당 행에서 order_id 추출
            order_id = row.locator("td[data-testid='order']").get_attribute('data-orderid')  # data-orderid를 정확히 지정
            print(f"찾은 order_id: {order_id}")
            return order_id

    # 만약 해당 제품이 없으면 None 반환
    return None


# Playwright 실행 예시
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URLS["bay_login"])  # 실제 테스트할 페이지 URL로 변경
    page.fill("data-testid=input_id", Account["testid"])  # 아이디 입력
    page.fill("data-testid=input_pw", Account["testpw"])  # 비밀번호 입력
    page.click("data-testid=btn_login", timeout=30000)  # 로그인 버튼 클릭
    page.wait_for_timeout(3000)
    page.goto(URLS["bay_orderList"])


    product_name = "제품 50"  # 테스트할 제품

    page.fill("data-testid=input_search", product_name)
    page.click("data-testid=btn_search")
    page.wait_for_timeout(3000)
    orderid = get_order_id_from_order_list(page, product_name)
    
    if orderid:
        print(f"찾은 제품의 orderid: {orderid}")
    else:
        print("제품을 찾을 수 없습니다.")

    browser.close()
