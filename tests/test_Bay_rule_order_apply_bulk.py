from playwright.sync_api import Page, expect
from helpers.common_utils import bay_login
from config import URLS
import json
import datetime
PRODUCT_FILE_PATH = "product_name.json"

def update_order_rule(prdname_list):
    try:
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        products = []

    updated = 0
    for product in products:
        if product.get("kor").strip() in [p.strip() for p in prdname_list]:
            product["order_rule"] = "일괄 적용 확인 규칙"
            updated += 1

    # 업데이트된 내용 저장
    with open(PRODUCT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"📝 JSON 업데이트 완료: {updated}건 수정됨")

def load_excel_products(json_path="product_name.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # "register": "excel" 인 제품만 필터링
    excel_products = [p for p in products if p.get("register") == "excel"]

    print(f"✅ excel_products 로드 완료: {len(excel_products)}개")
    return excel_products

def test_apply_rule_order_bulk(page:Page):
    bay_login(page, "admin")
    page.goto(URLS["bay_rules"])
    page.wait_for_timeout(2000)

    rule_name = "일괄 적용 확인 규칙"

    page.locator("data-testid=btn_register_bulk").click()
    page.wait_for_selector("data-testid=drop_rule_trigger", timeout=5000)

    page.locator("data-testid=drop_rule_trigger").click()
    page.wait_for_selector("data-testid=drop_rule_search", timeout=3000)
    page.locator("data-testid=drop_rule_search").fill(rule_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=drop_rule_item", has_text=rule_name).click()
    page.wait_for_timeout(1000)

    today = datetime.date.today()
    mmdd = today.strftime("%m%d")
    today_products = f"엑셀업로드_{mmdd}"

    page.locator("data-testid=input_search").fill(today_products)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    excel_products = load_excel_products()
    excel_count = len(excel_products)
    

    prdname_list = [product.get("kor") for product in excel_products]
    row_count = rows.count()
    found = False

    for i in range(row_count):
        cell_text = rows.nth(i).locator("td").nth(3).inner_text().strip()  # 4열 값

        cell_kor_name = cell_text.split("\n")[0].strip()

        if cell_kor_name in prdname_list: 
            checkbox = rows.nth(i).locator("td").nth(0)
            checkbox.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            checkbox.click()
            page.wait_for_timeout(300)
            print(f"✅ {i+1}행: '{cell_kor_name}' 일치 → 체크박스 클릭 완료")
            found = True

    if not found:
        print("⚠️ 등록된 제품명과 일치하는 행을 찾지 못함")

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_title")).to_have_text(f"{excel_count}개 제품의 발주 규칙을 일괄 적용하시겠습니까?", timeout=3000)
    expect(page.locator("data-testid=txt_subtitle")).to_have_text("일괄 적용되며, 승인 및 발주 중인 제품은 다음 출고부터 적용됩니다.", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_rule_bulk")).to_have_text("발주 규칙 일괄 적용이 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=input_search", timeout=5000)
    page.locator("data-testid=input_search").fill(cell_kor_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    rule_cell = rows.nth(0).locator('td:nth-child(9)') #1행 9열
    rule_text = rule_cell.inner_text().strip()
    assert rule_name == rule_text, f"발주 규칙 적용 되지 않음 (노출 값: {rule_text})"

    update_order_rule(prdname_list)

