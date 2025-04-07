import requests
from playwright.sync_api import Page, sync_playwright
from config import URLS, Account

def get_order_url_from_api(order_id: str) -> str:
    # 내부 API 호출하여 발주 수락 URL을 받아옴
    api_url = f"http://example.com/api/get_order_url/{order_id}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        order_url = response.json().get('url') 
        return order_url
    else:
        raise Exception(f"API 호출 실패: {response.status_code}")

def test_order_acceptance_with_url(page: Page, order_url: str):
    page.goto(order_url) 

    page.fill("input[data-testid='input_name']", "권정의")
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.click("button[data-testid='btn_confirm']")  
    page.click("button[data-testid='btn_accept']")  
   
    page.goto(URLS["bay_orderList"])
    page.wait_for_selector("h1")
    page_content = page.inner_text("h1")

    assert "발주 진행" in page_content, "발주 진행 상태가 아닙니다."


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 내부 API에서 URL을 받아옴
    order_id = "ORDER_ID"  # 테스트할 주문 ID
    order_url = get_order_url_from_api(order_id)
    
    test_order_acceptance_with_url(page, order_url)
    
    browser.close()
