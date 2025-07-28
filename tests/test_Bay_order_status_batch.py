# 배치 발주로 인해 발주 내역이 생성된 항목들 확인
# 제품1~3: 발주 취소 확인
# 제품4~6: 발송진행 + 일부수령 + 수령완료 확인
# 제품7~9: 배송진행 + 일부수령 + 수령완료 확인

import random
from config import URLS, Account
from datetime import datetime, timedelta
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import search_order_history,get_order_id_from_order_list, check_order_status_by_order_id
from helpers.common_utils import bay_login
from playwright.sync_api import Page, expect
import time
product_list = [f"자동화제품_{i}" for i in range(1, 10)]

def accept_order(page:Page, order_id:str, manager:str):
    accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
    page.goto(accept_url)
    page.wait_for_timeout(2000)
    if manager == "권정의":
        page.fill("input[data-testid='input_name']", "권정의")
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", "01062754153")
        page.wait_for_timeout(1000)
    else :
        page.fill("input[data-testid='input_name']", "메디솔브")
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", "01085148780")
        page.wait_for_timeout(1000)
    page.locator("button[data-testid='btn_confirm']").last.click()
    expect(page.locator("data-testid=btn_accept")).to_be_visible(timeout=5000)
    page.wait_for_timeout(1000)
    page.click("button[data-testid='btn_accept']")
    expect(page.locator("data-testid=toast_accept")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

def delivery_order(page:Page, order_id:str, manager:str):
    delivery_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
    page.goto(delivery_url)
    page.wait_for_timeout(2000)
    if manager == "권정의":
        page.fill("input[data-testid='input_name']", "권정의")
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", "01062754153")
        page.wait_for_timeout(1000)
    else :
        page.fill("input[data-testid='input_name']", "메디솔브")
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", "01085148780")
        page.wait_for_timeout(1000)

    page.locator("button[data-testid='btn_confirm']").last.click()
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

def test_cancel_batch_history(page:Page):
    prd_name = f"{product_list[0]} 외 2건"

    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)

    order_id = search_order_history(page, product_list[2], "발주 요청")
    page.wait_for_timeout(1000)
    
    cell_locator = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=1") #1행 2열 
    expect(cell_locator).to_have_text("자동화제품_1 외 2건", timeout=3000)

    # 상세 버튼 클릭
    page.locator("data-testid=btn_detail").click()
    page.wait_for_timeout(1000)
    products = ["자동화제품_1", "자동화제품_2", "자동화제품_3"]

    for i, text in enumerate(products, start=1):  # 2행부터 확인
        detail_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=1")
        expect(detail_locator).to_have_text(text, timeout=3000)

    page.wait_for_timeout(1000)
    cancel_index = random.randint(1, 3)  # (2~4행)
    cancel_target = products[cancel_index - 1]
    print(f"취소 대상 제품: {cancel_target} (tr index={cancel_index})")
    cancel_txt = "발주를 취소하시겠습니까?"

    # 1개만 취소 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        name_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=1")
        expect(name_locator).to_have_text(product_name, timeout=3000)

        if i == cancel_index:
            cancel_button = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> [data-testid=btn_cancel]")
            cancel_button.click()
            page.wait_for_timeout(1000)
            expect(page.locator("data-testid=txt_cancel")).to_have_text(cancel_txt, timeout=3000)
            page.wait_for_timeout(1000)
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=toast_cancel")).to_be_visible(timeout=3000)
            page.wait_for_timeout(3000)

    for i in range(4):  # tr index 0~3 → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        if i == cancel_index:
            expect(status_locator).to_have_text("발주 취소", timeout=3000)
        else:
            expect(status_locator).to_have_text("발주 요청", timeout=3000)
    
    # 발주 요청 상태(발주 요청+발주 취소) UI 확인
    expected_status_conditions = order_status_map["발주 요청"]  
    check_order_status_by_order_id(page, "발주 요청", order_id, expected_status_conditions)
    
    # 일괄 취소 후 상태 확인
    bulk_cancel_txt = "발주를 일괄 취소하시겠습니까?"
    cancel_button = page.locator("data-testid=history >> tr >> nth=0 >> td >> [data-testid=btn_cancel]")
    cancel_button.click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_cancel_bulk")).to_have_text(bulk_cancel_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_cancel_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(3000)

    for i in range(4):  # → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        expect(status_locator).to_have_text("발주 취소", timeout=3000)
        page.wait_for_timeout(1000)
    
    # 발주 취소 상태 UI 확인
    expected_status_conditions = order_status_map["발주 취소"]  
    check_order_status_by_order_id(page, "발주 취소", order_id, expected_status_conditions)

def test_receive_without_tracking(page:Page):
    prd_name = f"{product_list[3]} 외 2건"
    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[5], "발주 요청")
    order_id = get_order_id_from_order_list(page, prd_name)
    products = ["자동화제품_4", "자동화제품_5", "자동화제품_6"]
    accept_order(page, order_id, "메디솔브")

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[5], "발주 진행")

    page.locator("data-testid=btn_detail").click()
    page.wait_for_timeout(1000)
    # 발주 진행 상태 확인
    for i in range(4):  # → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        expect(status_locator).to_have_text("발주 진행", timeout=3000)
        page.wait_for_timeout(1000)
    
    receive_index = random.randint(1, 3)  # (2~4행)
    receive_target = products[receive_index - 1]
    print(f"수령 확정 대상 제품: {receive_target} (tr index={receive_index})")

    # 1개만 수령확정 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        name_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=1")
        expect(name_locator).to_have_text(product_name, timeout=3000)

        if i == receive_index:
            receive_button = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> [data-testid=btn_receive]")
            receive_button.click()
            expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
            page.locator("data-testid=btn_confirm").click()
            page.wait_for_timeout(3000)

    summary_status = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=0")
    expect(summary_status).to_have_text("일부 수령", timeout=3000)

    for i in range(1, 4):  # tr index 1~3
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        if i == receive_index:
            expect(status_locator).to_have_text("수령 완료", timeout=3000)
        else:
            expect(status_locator).to_have_text("발주 진행", timeout=3000)
        
    # 일부 수령 상태 UI 확인
    expected_status_conditions = order_status_map["일부 수령"]
    check_order_status_by_order_id(page, "일부 수령", order_id, expected_status_conditions)

    # 일괄 수령 후 상태 확인
    bulk_receive_txt = "발주를 일괄 수령하시겠습니까?"
    receive_button = page.locator("data-testid=history >> tr >> nth=0 >> td >> [data-testid=btn_receive]")
    receive_button.click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_receive_bulk")).to_have_text(bulk_receive_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_receive_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    for i in range(4):  # → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        expect(status_locator).to_have_text("수령 완료", timeout=3000)
        page.wait_for_timeout(1000)

    # 수령 완료 상태 UI 확인
    expected_status_conditions = order_status_map["수령 완료"]
    check_order_status_by_order_id(page, "수령 완료", order_id, expected_status_conditions)
    
def test_receive_with_tracking(page:Page):
    prd_name = f"{product_list[6]} 외 2건"
    bay_login(page)
    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[8], "발주 요청")

    order_id = get_order_id_from_order_list(page, prd_name)
    products = ["자동화제품_7", "자동화제품_8", "자동화제품_9"]
    accept_order(page, order_id, "권정의")
    delivery_order(page, order_id, "권정의")

    page.goto(URLS["bay_orderList"])
    page.wait_for_timeout(2000)
    search_order_history(page, product_list[8], "배송 진행")

    page.locator("data-testid=btn_detail").click()
    page.wait_for_timeout(1000)
    # 배송 진행 상태 확인
    for i in range(4):  # → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        expect(status_locator).to_have_text("배송 진행", timeout=3000)
        page.wait_for_timeout(1000)
    
    receive_index = random.randint(1, 3)  # (2~4행)
    receive_target = products[receive_index - 1]
    print(f"수령 확정 대상 제품: {receive_target} (tr index={receive_index})")

    # 1개만 수령확정 후 상태 확인
    for i, product_name in enumerate(products, start=1):  # tr 1~3 (2~4행)
        name_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=1")
        expect(name_locator).to_have_text(product_name, timeout=3000)

        if i == receive_index:
            receive_button = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> [data-testid=btn_receive]")
            receive_button.click()
            expect(page.locator("data-testid=drop_prdname_trigger")).to_be_visible(timeout=3000)
            page.locator("data-testid=btn_confirm").click()
            page.wait_for_timeout(3000)

    summary_status = page.locator("data-testid=history >> tr >> nth=0 >> td >> nth=0")
    expect(summary_status).to_have_text("일부 수령", timeout=3000)

    for i in range(1, 4):  # tr index 1~3
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        if i == receive_index:
            expect(status_locator).to_have_text("수령 완료", timeout=3000)
        else:
            expect(status_locator).to_have_text("배송 진행", timeout=3000)
    
    # 일부 수령 상태 UI 확인
    expected_status_conditions = order_status_map["일부 수령"]
    check_order_status_by_order_id(page, "일부 수령", order_id, expected_status_conditions)
    
    # 일괄 수령 후 상태 확인
    bulk_receive_txt = "발주를 일괄 수령하시겠습니까?"
    receive_button = page.locator("data-testid=history >> tr >> nth=0 >> td >> [data-testid=btn_receive]")
    receive_button.click()
    page.wait_for_timeout(1000)
    expect(page.locator("data-testid=txt_receive_bulk")).to_have_text(bulk_receive_txt, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_confirm").click()
    expect(page.locator("data-testid=toast_receive_bulk")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    for i in range(4):  # → 1~4행
        status_locator = page.locator(f"data-testid=history >> tr >> nth={i} >> td >> nth=0")
        expect(status_locator).to_have_text("수령 완료", timeout=3000)
        page.wait_for_timeout(1000)

    # 수령 완료 상태 UI 확인
    expected_status_conditions = order_status_map["수령 완료"]
    check_order_status_by_order_id(page, "수령 완료", order_id, expected_status_conditions)


