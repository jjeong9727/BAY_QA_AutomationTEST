from playwright.sync_api import Page, sync_playwright
from config import URLS

def test_order_acceptance_and_tracking(page: Page):
    # 1. 발주 내역 화면으로 이동
    page.goto(URLS["bay_orderList"])
    
    # 2. 최상단에 노출되는 제품명을 저장
    product_name = page.inner_text("table tr:first-child td:nth-child(2)")  # 제품명은 2열에 있다고 가정
    
    # 3. 해당 제품의 order_id 값을 히든 필드나 다른 방식으로 가져옴
    order_id = page.get_attribute("table tr:first-child td:nth-child(2) input[type='hidden']", "value")
    
    # 4. URL에 order_id를 조합하여 발주 수락 화면으로 진입
    order_url = f"{URLS['base_url']}/providers/orders/{order_id}"
    page.goto(order_url)
    
    # 5. 본인 인증
    page.fill("input[data-testid='input_name']", "권정의")
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.click("button[data-testid='btn_confirm']")  # 인증 버튼 클릭
    page.wait_for_timeout(1500)
    page.click("button[data-testid='btn_confirm']")  # 수락 버튼 클릭

    # 6. 운송장 등록 URL 진입
    # 발주 수락 화면에서 택배사 드롭다운 선택 및 운송장 번호 입력
    page.select_option("select[data-testid='drop_shipping']", label="택배사 A")
    page.fill("input[data-testid='input_tracking']", "1234567890")
    
    # 등록 버튼 클릭
    page.click("button[data-testid='btn_confirm']")  # 등록 버튼 클릭

    # 7. 발주 내역 화면으로 돌아가서 제품명으로 상태 확인
    page.goto(URLS["bay_orderList"])
    
    # 8. 저장한 제품명으로 검색
    page.fill("input[data-testid='search_order']", product_name)
    page.click("button[data-testid='btn_search']")
    
    # 발주 상태 확인
    page.wait_for_selector("h1")
    page_content = page.inner_text("h1")

    # "배송 진행" 상태 확인
    if "배송 진행" in page_content:
        print("PASS")
    else:
        print("FAIL")

# Playwright 실행 예시
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    test_order_acceptance_and_tracking(page)
    
    browser.close()
