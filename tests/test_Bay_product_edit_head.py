from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.product_utils import verify_product_update
from helpers.product_utils import update_product_flag
from helpers.common_utils import bay_login

edit_product = "수정 확인 제품"
# 제품 수정 확인
def test_edit_products(page):
    bay_login(page)

    page.goto(URLS["bay_prdList"])
    page.wait_for_selector("data-testid=btn_addprd", timeout=5000)

    page.locator("data-testid=input_search").fill(edit_product)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)

    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    product_value = first_row.locator("td:nth-child(3)").inner_text().strip()

    if product_value == "수정 확인 제품":
        new_name = "[수정] 수정 확인 제품"
    else:
        new_name = "수정 확인 제품"

    edit_button = first_row.locator("td:last-child >> text=수정")
    edit_button.click()
    page.wait_for_selector("data-testid=input_prdname_kor", timeout=5000)

    page.locator("data-testid=input_prdname_kor").fill(new_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_save").click()
    expect(page.locator("data-testid=txt_edit")).to_have_text("제품을 수정하시겠습니까?", timeout=3000)
    expect(page.locator("data-testid=txt_subtitle")).to_have_text("확인 시, 해당 제품이 사용된 모든 영역이 변경됩니다.", timeout=3000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_edit")).to_have_text("제품 수정이 완료되었습니다.", timeout=3000)
    page.wait_for_timeout(1000)

    page.locator("data-testid=input_search").fill(new_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_search").click()
    page.wait_for_timeout(2000)
    rows = page.locator("table tbody tr")
    first_row = rows.nth(0)
    product_value = first_row.locator("td:nth-child(3)").inner_text().strip()
    assert product_value == new_name, f"제품 수정한 값과 다르게 노출됨 기대값: {new_name}, 실제 값: {product_value}"

    