# 배치 발주로 인해 발주 내역이 생성된 항목들 확인
# 제품1~3: 발주 취소 확인
# 제품4~6: 발송진행 + 일부수령 + 수령완료 확인
# 제품7~9: 배송진행 + 일부수령 + 수령완료 확인

import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import search_order_history,get_order_id_from_order_list, check_order_status_by_order_id_bulk
from helpers.common_utils import bay_login
from helpers.approve_utils import check_approval_status_buttons
from playwright.sync_api import Page, expect
import json
from pathlib import Path
import time

BATCH_PATH = Path("batch_time.json")
def load_batch_time(path: Path = BATCH_PATH) -> tuple[str, str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj["hour"], obj["minute"]  # "HH", "MM"
hour_str, minute_str = load_batch_time()
def is_target_passed_now(hour_str: str, minute_str: str) -> bool:
    now = datetime.now()
    target_today = now.replace(
        hour=int(hour_str), minute=int(minute_str), second=0, microsecond=0
    )
    return now >= target_today

if not is_target_passed_now(hour_str, minute_str):
    # 아직 안 지났으면 목표 시각 + 1분까지 대기
    
    now = datetime.now()
    target = now.replace(hour=int(hour_str), minute=int(minute_str), second=0, microsecond=0)
    time.sleep(max(0, (target - now).total_seconds()) + 60)  # +60s 여유

product_list = [f"자동화제품_{i}" for i in range(1, 10)]

def accept_order(page:Page, order_id:str, manager:str):
    accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
    quantity = "총 3건"
    page.goto(accept_url)
    page.wait_for_timeout(2000)
    page.fill("input[data-testid='input_name']", manager)
    page.wait_for_timeout(1000)
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.wait_for_timeout(1000)
    page.locator("button[data-testid='btn_confirm']").click()
    # 발주 규칙에 따른 제품 개수 확인(3개 고정)
    expect(page.locator("data-testid=txt_quantity")).to_have_text(quantity, timeout=7000)
    page.wait_for_timeout(1000)
    page.locator("button[data-testid='btn_accept']").last.click()
    expect(page.locator("data-testid=toast_accept")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

def delivery_order(page:Page, order_id:str, manager:str):
    delivery_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
    page.goto(delivery_url)
    page.wait_for_timeout(2000)
    page.fill("input[data-testid='input_name']", manager)
    page.wait_for_timeout(1000)
    page.fill("input[data-testid='input_contact']", "01062754153")
    page.wait_for_timeout(1000)
    page.locator("button[data-testid='btn_confirm']").click()

    expect(page.locator("data-testid=drop_shipping_trigger")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)
    carrier_name = "CJ대한통운"
    tracking = "1234567890"
    page.locator("data-testid=drop_shipping_trigger").click()
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_shipping_search").fill(carrier_name)
    page.wait_for_timeout(1000)
    page.locator("data-testid=drop_shipping_item", has_text=carrier_name).click()
    page.wait_for_timeout(1000)
    
    page.fill("input[data-testid='input_tracking']", tracking)
    page.wait_for_timeout(3000)
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=toast_tracking")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
# ✅ 발주 요청 -> 개별 취소 / 일괄 취소 
def test_cancel_batch_history(page:Page):
    
    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)

    search_order_history(page, product_list[2],"발주 요청")
    
    # 대표 내역 확인 후 order_id 추출 
    products = ["자동화제품_1", "자동화제품_2", "자동화제품_3"]
    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    order_cell = rows.nth(0).locator('td:nth-child(2)')
    main_product_name = order_cell.inner_text()
    order_id = get_order_id_from_order_list(page, main_product_name)

    print(f"orderID : {order_id}")
    page.wait_for_timeout(1000)
    
    rows.nth(0).locator("[data-testid='btn_detail']").click()
    page.wait_for_timeout(1000)

    cancel_index = random.randint(1, 3)  # (2~4행)
    cancel_target = products[cancel_index - 1]
    print(f"취소 대상 제품: {cancel_target} ")
    cancel_txt = "발주를 취소하시겠습니까?"

    # 1개만 취소 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        cancel_row = rows.nth(i)

        if i == cancel_index:
            # 🔽 해당 행의 취소 버튼 클릭
            rows.nth(i).locator('[data-testid="btn_order_cancel"]').click()
            expect(page.locator("data-testid=txt_cancel")).to_have_text(cancel_txt, timeout=3000)

            page.wait_for_timeout(1000)
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=toast_cancel")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

    # 🔍 상태 확인 (상세 내역)
    for i in range(1,4):  # tr index 1~3 ⇒ 2~4행
        # 🔽 order 셀 기준으로 해당 tr의 상태 셀(td[1]) 접근
        first_history = page.locator('[data-testid="history"]').first
        rows = first_history.locator('table tbody tr')
        cancel_row = rows.nth(i)
        status_cell = cancel_row.locator('td:nth-child(1)')

        if i == cancel_index:
            expect(status_cell).to_have_text("발주 취소", timeout=3000)

        else:
            expect(status_cell).to_have_text("발주 요청", timeout=3000)
        page.wait_for_timeout(1000)
        
    
    # 일괄 취소 후 상태 확인
    bulk_cancel_txt = "발주를 일괄 취소하시겠습니까?"
    page.locator("data-testid=btn_order_cancel").nth(0).click()
    expect(page.locator("data-testid=txt_cancel_bulk")).to_have_text(bulk_cancel_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_cancel_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(3000)

    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(2000)

    search_order_history(page, product_list[2],"발주 취소")
    page.wait_for_selector("[data-testid='history']", timeout=5000)

    for i in range(4):  # → 1~4행
        first_history = page.locator('[data-testid="history"]').first
        rows = first_history.locator('table tbody tr')
        order_row = rows.nth(i)
        status_cell = order_row.locator('td:nth-child(1)')
        expect(status_cell).to_have_text("발주 취소", timeout=3000)
        page.wait_for_timeout(1000)
    
    # 발주 취소 상태 UI 확인
    expected_status_conditions = order_status_map["발주 취소"]  
    check_order_status_by_order_id_bulk(page, "발주 취소", order_id, expected_status_conditions)

# ✅ 발주 진행 -> 일부 수령 -> 수령 완료
def test_receive_without_tracking(page:Page):

    # 대표 내역 확인 후 order_id 추출 
    products = ["자동화제품_4", "자동화제품_5", "자동화제품_6"]

    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[5], "발주 요청")
    page.wait_for_selector("[data-testid='history']", timeout=5000)


    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    order_cell = rows.nth(0).locator('td:nth-child(2)')
    main_product_name = order_cell.inner_text()
    order_id = get_order_id_from_order_list(page, main_product_name)

    print(f"orderID : {order_id}")
    page.wait_for_timeout(1000)
    
    accept_order(page, order_id, "권정의E")

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[5], "발주 진행")
    page.wait_for_selector("[data-testid='history']", timeout=5000)

    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)

    # 발주 진행 상태 확인
    for i in range(4):  # → 1~4행
        first_history = page.locator('[data-testid="history"]').first
        rows = first_history.locator('table tbody tr')
        receive_cell = rows.nth(i)
        status_cell = receive_cell.locator('td:nth-child(1)')
        expect(status_cell).to_have_text("발주 진행", timeout=3000)
        page.wait_for_timeout(1000)
    
    receive_index = random.randint(1, 3)  # (2~4행)
    receive_target = products[receive_index - 1]
    print(f"수령 확정 대상 제품: {receive_target} ")

    # 1개만 수령확정 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        order_cell = rows.nth(i)

        if i == receive_index:
            rows.nth(i).locator('[data-testid="btn_receive"]').click()
            expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
            page.locator("data-testid=btn_confirm").click()
            page.wait_for_timeout(3000)
    
    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)
    search_order_history(page, product_list[5], "일부 수령")
    page.wait_for_selector("[data-testid='history']", timeout=5000)

    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)
    

    for i in range(1, 4):  # tr index 1~3 / 2~4행
        order_cell = rows.nth(i)
        status_cell = order_cell.locator('td:nth-child(1)')
        if i == receive_index:
            expect(status_cell).to_have_text("수령 완료", timeout=3000)
        else:
            expect(status_cell).to_have_text("발주 진행", timeout=3000)
        page.wait_for_timeout(1000)
        
    # 일부 수령 상태 UI 확인
    expected_status_conditions = order_status_map["일부 수령(배송전)"]
    check_order_status_by_order_id_bulk(page, "일부 수령", order_id, expected_status_conditions)

    # 일괄 수령 후 상태 확인
    bulk_receive_txt = "발주를 일괄 수령하시겠습니까?"
    page.locator("data-testid=btn_receive").nth(0).click()
    expect(page.locator("data-testid=txt_receive_bulk")).to_have_text(bulk_receive_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_receive_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(3000)

    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)

    search_order_history(page, product_list[5], "수령 완료")
    page.wait_for_selector("[data-testid='history']", timeout=5000)
    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)

    for i in range(4):  # → 1~4행
        order_cell = rows.nth(i)
        status_cell = rows.nth(i).locator('td:nth-child(1)')
        expect(status_cell).to_have_text("수령 완료", timeout=3000)
        page.wait_for_timeout(1000)

    # 수령 완료 상태 UI 확인
    expected_status_conditions = order_status_map["수령 완료(배송전)"]
    check_order_status_by_order_id_bulk(page, "수령 완료", order_id, expected_status_conditions)

# ✅ 배송 진행 -> 일부 수령 -> 수령 완료    
def test_receive_with_tracking(page:Page):
    products = ["자동화제품_7", "자동화제품_8", "자동화제품_9"]

    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[8], "발주 요청")
    page.wait_for_selector("[data-testid='history']", timeout=5000)

    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    order_cell = rows.nth(0).locator('td:nth-child(2)')
    main_product_name = order_cell.inner_text()
    order_id = get_order_id_from_order_list(page, main_product_name)

    print(f"orderID : {order_id}")
    page.wait_for_timeout(1000)
    
    accept_order(page, order_id, "권정의F")
    delivery_order(page, order_id, "권정의F")

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[8], "배송 진행")
    page.wait_for_selector("[data-testid='history']", timeout=5000)

    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)

    # 배송 진행 상태 확인
    for i in range(4):  # → 1~4행
        order_cell = rows.nth(i)
        status_cell = order_cell.locator('td:nth-child(1)')
        expect(status_cell).to_have_text("배송 진행", timeout=3000)
        page.wait_for_timeout(1000)
    
    receive_index = random.randint(1, 3)  # (2~4행)
    receive_target = products[receive_index - 1]
    print(f"수령 확정 대상 제품: {receive_target} ")

    # 1개만 수령확정 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        order_cell = rows.nth(i)

        if i == receive_index:
            rows.nth(i).locator('[data-testid="btn_receive"]').click()
            expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
            page.locator("data-testid=btn_confirm").click()
            page.wait_for_timeout(3000)

    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)
    search_order_history(page, product_list[8], "일부 수령")
    page.wait_for_selector("[data-testid='history']", timeout=5000)
    
    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)

    for i in range(1, 4):  # tr index 1~3 / 2~4행
        order_cell = rows.nth(i)
        status_cell = order_cell.locator('td:nth-child(1)')
        if i == receive_index:
            expect(status_cell).to_have_text("수령 완료", timeout=3000)
        else:
            expect(status_cell).to_have_text("배송 진행", timeout=3000)
        page.wait_for_timeout(1000)
    
    # 일부 수령 상태 UI 확인
    expected_status_conditions = order_status_map["일부 수령(배송후)"]
    check_order_status_by_order_id_bulk(page, "일부 수령", order_id, expected_status_conditions)

    # 일괄 수령 후 상태 확인
    bulk_receive_txt = "발주를 일괄 수령하시겠습니까?"
    page.locator("data-testid=btn_receive").nth(0).click()
    expect(page.locator("data-testid=txt_receive_bulk")).to_have_text(bulk_receive_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_receive_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(3000)

    page.locator("data-testid=btn_reset").click()
    page.wait_for_timeout(3000)

    search_order_history(page, product_list[8], "수령 완료")
    page.wait_for_selector("[data-testid='history']", timeout=5000)
    first_history = page.locator('[data-testid="history"]').first
    rows = first_history.locator('table tbody tr')
    rows.nth(0).locator('[data-testid="btn_detail"]').click()
    page.wait_for_timeout(1000)

    for i in range(4):  # → 1~4행
        order_cell = rows.nth(i)
        status_cell = rows.nth(i).locator('td:nth-child(1)')
        expect(status_cell).to_have_text("수령 완료", timeout=3000)
        page.wait_for_timeout(1000)

    # 수령 완료 상태 UI 확인
    expected_status_conditions = order_status_map["수령 완료(배송후)"]
    check_order_status_by_order_id_bulk(page, "수령 완료", order_id, expected_status_conditions)

    # 수령완료 후 발주 예정 내역의 "수령완료"상태 확인
    check_approval_status_buttons(page, "수령 완료", product_list[8], "자동화규칙_묶음", True, False)