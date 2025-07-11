from playwright.sync_api import Page, expect
import random
from config import URLS, Account
from helpers.product_utils import append_product_name, generate_product_names, verify_products_in_list
from helpers.common_utils import bay_login

edit_name = "수정테스트"

def test_check_alert(page:Page):
    bay_login(page)
    # [카테고리 관리] 이탈 팝업 확인
    page.goto(URLS["bay_category"])
    page.wait_for_timeout(2000)
    # 구분 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_category").click()
    expect(page.locator("data-testid=txt_nosave")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)
    # 종류 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_maker").click()
    expect(page.locator("data-testid=txt_nosave")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000) 
    # 제조사 탭
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_type").click()
    expect(page.locator("data-testid=txt_nosave")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    page.wait_for_timeout(1000)
    # 구분 탭에서 이탈 취소 확인
    page.locator("data-testid=input_kor").first.fill(edit_name)
    page.wait_for_timeout(500)
    page.locator("data-testid=tab_category").click()
    expect(page.locator("data-testid=txt_nosave")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_cancel").click()
    expect(page.locator("data-testid=input_kor").first).to_have_value(edit_name, timeout=3000)
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
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=input_prdname_kor").first).to_have_value(edit_name, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
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
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=drop_maker_trigger")).to_have_text("중복테스트", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
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
    expect(page.locator('[data-testid="txt_register"]')).to_have_text(txt_register,timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator('[data-testid="toast_over_stock"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
 
    # 이탈 팝업 확인
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(page.locator("data-testid=input")).to_have_value("테스트 메모", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_back").click()
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=btn_stockadd")).to_be_visible(timeout=3000)
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
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_no").click()
    expect(input_field).to_have_value("100", timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_stockadd").click()
    expect(page.locator("data-testid=title")).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    page.locator("data-testid=btn_yes").click()
    expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)


    
    


