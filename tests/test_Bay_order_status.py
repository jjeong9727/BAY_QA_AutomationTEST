import json
import re
from datetime import datetime, timedelta
import time
import random
from pathlib import Path
from playwright.sync_api import Page, sync_playwright, expect
from config import URLS, Account
from helpers.order_status_utils import (
    filter_products_by_delivery_status, get_order_id_from_order_list, check_order_status_by_order_id,
    search_order_history
)
from helpers.approve_utils import check_approval_status_buttons
from helpers.order_status_data import order_status_map
from helpers.common_utils import bay_login
# 배치 시간(+1분) 까지 대기
def wait_until_batch_ready(json_path="batch_time.json"):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    if "next_time" in data and data["next_time"]:  # full datetime 우선
        next_time = datetime.strptime(data["next_time"], "%Y-%m-%d %H:%M:%S")
    else:  # hour/minute 기반
        now = datetime.now()
        next_time = now.replace(hour=int(data["hour"]), minute=int(data["minute"]),
                                second=0, microsecond=0)

    deadline = next_time + timedelta(minutes=1)
    now = datetime.now()

    print(f"⏰ 현재 시간:   {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📌 배치 시간:   {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ 최소 실행 시: {deadline.strftime('%Y-%m-%d %H:%M:%S')}")

    if now < deadline:
        wait_seconds = (deadline - now).total_seconds()
        print(f"⏳ {wait_seconds:.0f}초 대기 후 테스트 시작")
        time.sleep(wait_seconds)

    print("✅ 조건 충족! 테스트를 시작합니다.")

# 발주 취소 확인 
def test_order_cancel(page: Page):
    product_name = "자동화개별제품_1"
    try:
        # 배치 발주 시간+1분 까지 대기 
        wait_until_batch_ready("batch_time.json")

        bay_login(page, "jekwon")

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        search_order_history(page, product_name, "발주 요청")

        # 검색된 제품의 order_id 값 가져오기
        order_id = get_order_id_from_order_list(page, product_name)
        
        if not order_id:
            raise ValueError(f"Order ID for product {product_name} not found")

        # 취소 버튼
        txt_cancel = "발주를 취소하시겠습니까?"
        page.locator("data-testid=btn_order_cancel").click()  # 취소 버튼 클릭
        expect(page.locator("data-testid=txt_cancel")).to_have_text(txt_cancel, timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_confirm").click()  
        expect(page.locator("data-testid=toast_cancel")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        # 발주 내역에서 해당 제품을 "발주 취소" 상태인지 확인
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                print(f"[PASS] 발주 취소 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # # 발주 진행 상태 확인 후 delivery_status 값을 5로 업데이트 (발주 취소 상태)
        # update_product_status_in_json(product_name=product_name, delivery_status=5, order_flag=0)  # delivery_status를 5로 업데이트 (발주 취소), order_flag=0

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["발주 취소"]  # 발주 취소 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "발주 취소", order_id, expected_status_conditions)

    except Exception as e:
        error_message = f"❌ Error in test_order_cancel: {str(e)}"
        print(error_message)
        raise  # Reraise the exception to maintain test flow

# 발주 실패 UI 확인 
def test_order_status_fail(page: Page):
    status_name = "발주 실패"
    try:
        filtered_products = filter_products_by_delivery_status(6)
        if not filtered_products:
            raise ValueError(f"[FAIL] '{status_name}' 상태의 제품이 없습니다.")

        # 무작위 제품 선택
        product = random.choice(filtered_products)
        product_name = product["kor"]

        bay_login(page, "jekwon")
         
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        page.locator("data-testid=drop_status_trigger").click()
        expect(page.locator("data-testid=drop_status_item")).to_be_visible(timeout=5000)
        page.locator('[role="option"]').filter(has_text="발주 실패").click()
        page.wait_for_timeout(1000)
        # 제품명 입력
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(500)
        # 검색 버튼 클릭
        page.locator("[data-testid=btn_search]").click()
        page.wait_for_timeout(2000)

        # 상태 확인
        expect(page.locator("[data-testid=btn_receive]")).to_be_disabled(timeout=3000)
        expect(page.locator("data-testid=btn_resend")).to_be_enabled(timeout=3000)
        expect(page.locator("data-testid=btn_order_cancel")).to_be_enabled(timeout=3000)
    except Exception as e:
        error_message = f"❌ Error in test_order_status_fail: {str(e)}"
        print(error_message)
        raise  # 예외 재전파로 테스트 실패 처리

# 발주 수락 
def test_order_acceptance(page: Page):
    status_name = "발주 요청"
    selected_products = ["자동화개별제품_2", "자동화개별제품_3"]
    names = ["권정의B", "권정의C"]
    phone = "01062754153"

    for product in selected_products:
        product_name = product
        if product == "자동화개별제품_2":
            name = names[0]
        else:
            name = names[1]

        try:
            # 로그인
            bay_login(page, "jekwon")

            # 발주 내역 검색
            page.goto(URLS["bay_orderList"])
            page.wait_for_timeout(2000)

            search_order_history(page, product_name, status_name)

            # order_id 추출
            order_id = get_order_id_from_order_list(page, product_name)
            if not order_id:
                raise ValueError(f"Order ID for '{product_name}'를 찾을 수 없습니다.")

            # 상태 확인
            expected_status_conditions = order_status_map["발주 요청"]
            check_order_status_by_order_id(page, "발주 요청", order_id, expected_status_conditions)

            # 재발송 확인
            txt_resend = "재발송하시겠습니까?"
            page.locator("data-testid=btn_resend").first.click()
            expect(page.locator("data-testid=txt_resend")).to_have_text(txt_resend, timeout=3000)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_confirm").click()
            expect(page.locator("data-testid=toast_resend")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

            # 수락 URL 접속 및 처리
            accept_url = f"{URLS['base_accept_url']}/{order_id}/accept"
            page.goto(accept_url)
            expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
            page.fill("input[data-testid='input_name']", name)
            page.wait_for_timeout(1000)
            page.fill("input[data-testid='input_contact']", phone)
            page.wait_for_timeout(1000)
            page.locator("button[data-testid='btn_confirm']").last.click()
            expect(page.locator("button[data-testid='btn_accept']")).to_be_visible(timeout=7000)
            page.wait_for_timeout(1000)
            page.click("button[data-testid='btn_accept']")
            expect(page.locator("data-testid=toast_accept")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

            # 발주 상태 재확인
            page.goto(URLS["bay_orderList"])
            expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
            page.wait_for_timeout(1000)
            page.fill("data-testid=input_search", product_name)
            page.wait_for_timeout(500)
            page.click("data-testid=btn_search")
            expect(page.locator("data-testid=history").first).to_be_visible(timeout=8000)
            page.wait_for_timeout(1000)

            rows = page.locator("table tbody tr")
            found = False
            for i in range(rows.count()):
                row = rows.nth(i)
                columns = row.locator("td").all_inner_texts()
                if product_name in columns[1]:
                    status = columns[0].strip()
                    assert status == "발주 진행", f"{product_name} 상태가 '발주 진행'이 아님 → 현재 상태: {status}"
                    print(f"[PASS] {product_name} → 발주 진행 상태 확인 완료")
                    found = True
                    break

            if not found:
                raise AssertionError(f"제품 '{product_name}'을 발주 내역에서 찾을 수 없습니다.")

            # # JSON 업데이트
            # update_product_status_in_json(product_name, 2)

            
        except Exception as e:
            print(f"❌ {product_name} 처리 중 오류 발생: {str(e)}")
            raise

# 운송장 등록
def test_order_delivery(page: Page):
    product_name = "자동화개별제품_2"
    name = "권정의B"
    phone = "01062754153"
    try:

        # 로그인
        bay_login(page, "jekwon")

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(2000)
        # search_order_history(page, product_name, "발주 진행")

        # # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 발주 상태 확인: '발주 진행'
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        # 배송 URL 진입
        tracking_url = f"{URLS['base_accept_url']}/{order_id}/delivery"
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)

        # 본인 인증
        page.fill("input[data-testid='input_name']", name)
        page.fill("input[data-testid='input_contact']", phone)
        page.click("button[data-testid='btn_confirm']")
        expect(page.locator("data-testid=drop_shipping_trigger")).to_be_visible(timeout=5000)

        # 배송사 선택 드롭다운 열기
        carrier_name = "일양로지스"
        tracking = "1234567890"
        new_carrier = "직접 배송"
        new_tracking = "직접 배송은 운송장 번호가 불필요합니다"
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


        # 상태 확인: 배송 진행
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(500)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(500)

        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "배송 진행", f"[FAIL] {product_name} 상태가 '배송 진행'이 아님 → 현재 상태: {status}"
                print(f"[PASS] 배송 진행 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break
        

        # 택배사 + 운송장 확인
        page.goto(URLS["bay_orderList"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=7000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(2000)
        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(carrier_name, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text(tracking, timeout=3000)
        page.wait_for_timeout(1000)

        page.locator("data-testid=btn_copy").click()
        expect(page.locator("data-testid=toast_copy")).to_have_text("운송장 번호가 복사되었습니다.", timeout=3000)

        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        # 운송정보 수정 후 확인 (직접 발주로 변경)
        page.goto(tracking_url)
        expect(page.locator("data-testid=input_name")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_name']", name)
        page.wait_for_timeout(1000)
        page.fill("input[data-testid='input_contact']", phone)
        page.wait_for_timeout(1000)
        page.click("button[data-testid='btn_confirm']")
        page.wait_for_timeout(1000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_trigger").click()
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_search").fill(new_carrier)
        page.wait_for_timeout(1000)
        page.locator("data-testid=drop_shipping_item", has_text=new_carrier).click()
        page.wait_for_timeout(1000)
        expect(page.locator("input[data-testid='input_tracking']")).to_have_attribute("placeholder", new_tracking, timeout=3000)
        page.locator("button[data-testid='btn_confirm']").last.click()
        expect(page.locator("data-testid=toast_edit")).to_be_visible(timeout=3000)
        page.wait_for_timeout(1000)

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        expect(page.locator("data-testid=history").first).to_be_visible(timeout=7000)
        page.wait_for_timeout(2000)

        page.locator("data-testid=btn_check_tracking").first.click()
        expect(page.locator("data-testid=txt_tracking")).to_have_text(new_carrier, timeout=3000)
        page.wait_for_timeout(1000)
        expect(page.locator("data-testid=txt_tracking_num")).to_have_text("-", timeout=3000)

        # 직접 배송인 경우 비활성화 
        expect(page.locator("data-testid=btn_copy")).to_be_disabled(timeout=3000)

        page.locator("data-testid=btn_confirm").click()
        page.wait_for_timeout(1000)

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

    except Exception as e:
        print(f"❌ Error in test_order_delivery: {str(e)}")
        raise

# 배송 진행 상태에서 수령
def test_order_receive_from_delivery(page: Page):
    try:
        product_name = "자동화개별제품_2"
        status_name = "배송 진행"

        bay_login(page, "jekwon")
        page.goto(URLS["bay_stock"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        first_row = page.locator("table tbody tr").first
        previous_stock_text = first_row.locator("td:nth-child(6)").inner_text()

        # 발주 내역 화면으로 이동하여 제품명 검색 
        page.goto(URLS["bay_orderList"])
        search_order_history(page, product_name, status_name)
        
        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID 확인 불가")

        # 확인할 상태에 대한 기대값을 설정
        expected_status_conditions = order_status_map["배송 진행"]  # 배송 진행 상태 조건을 설정

        # order_id를 사용하여 order status 확인
        check_order_status_by_order_id(page, "배송 진행", order_id, expected_status_conditions)

        # 수령확정 버튼(btn_receive)을 누르고 수령확인 버튼 클릭
        page.click("button[data-testid='btn_receive']")  # 수령 확정 버튼 클릭
        expect(page.locator("data-testid=input_quantity")).to_be_visible(timeout=5000)
        stock_inflow = int(page.locator('[data-testid="input_quantity"]').input_value())#입고 수량 저장
        print(stock_inflow)
        # 발주 수령 팝업 퀵메뉴 버튼 확인
        page.locator("data-testid=btn_plus_10").click()
        new_data = stock_inflow + 10
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_plus_100").click() 
        new_data += 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_100").click() 
        new_data -= 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_10").click() 
        new_data -= 10 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        assert new_data == stock_inflow, f"초기 수량과 동일하지 않음. 초기 수량: {stock_inflow}, 현재 수량: {new_data}"
        page.click("button[data-testid='btn_confirm']")  # 수령 확인 버튼 클릭
        page.wait_for_timeout(2000)

        
        # 발주 내역에서 해당 제품을 "수령 확정" 상태인지 확인
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000) 
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000) 
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:  # 제품명으로 해당 행 찾기
                status = columns[0].strip()  # 상태 확인
                print(f"[PASS] 수령 완료 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")

        # 재고 관리 화면으로 이동하여 제품명으로 검색
        page.goto(URLS["bay_stock"])
        expect(page.locator("data-testid=input_search")).to_be_visible(timeout=8000)
        page.wait_for_timeout(1000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(2000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        # 재고 관리 화면에서 해당 제품의 현 재고량 확인
        first_row = page.locator("table tbody tr").first
        current_stock_text = first_row.locator("td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        # JSON 파일에 있던 재고 수량 + 입고 수량 계산 후 비교
        expected_stock =  int(previous_stock_text)+ int(stock_inflow)

        assert current_stock == expected_stock, f"[FAIL] 현 재고량이 예상치와 다릅니다. 예상: {expected_stock}, 실제: {current_stock}"
        print(f"[PASS] 현 재고량 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

        # 수령완료 후 발주 예정 내역의 "수령완료"상태 확인
        check_approval_status_buttons(page, "수령 완료", product_name, "자동화규칙_개별", False, False)


    except Exception as e:
        error_message = f"❌ Error in test_order_receive_from_delivery: {str(e)}"
        print(error_message)

        # 실패한 테스트 결과를 저장
        raise  # Reraise the exception to maintain test flow

# 발주 진행 상태에서 수령 
def test_order_receive_from_progress(page: Page):
    try:
        product_name = "자동화개별제품_3"
        status_name = "발주 진행"

        bay_login(page, "jekwon")
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        previous_stock = page.locator("table tbody tr td:nth-child(6)").inner_text()

        page.goto(URLS["bay_orderList"])
        page.wait_for_timeout(1000)
        search_order_history(page, product_name, status_name)

        # order_id 추출
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"{product_name} 제품의 order ID를 찾을 수 없습니다.")

        # 상태 확인: 배송 진행
        expected_status_conditions = order_status_map["발주 진행"]
        check_order_status_by_order_id(page, "발주 진행", order_id, expected_status_conditions)

        
        # 수령확정 버튼(btn_receive)을 누르고 수령확인 버튼 클릭
        page.click("button[data-testid='btn_receive']")  # 수령 확정 버튼 클릭
        expect(page.locator("data-testid=input_quantity")).to_be_visible(timeout=5000)
        stock_inflow = int(page.locator('[data-testid="input_quantity"]').input_value())#입고 수량 저장
        print(stock_inflow)
        # 발주 수령 팝업 퀵메뉴 버튼 확인
        page.locator("data-testid=btn_plus_10").click()
        new_data = stock_inflow + 10
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_plus_100").click() 
        new_data += 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_100").click() 
        new_data -= 100 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_minus_10").click() 
        new_data -= 10 
        expect(page.locator("data-testid=input_quantity")).to_have_value(str(new_data), timeout=3000)
        page.wait_for_timeout(1000)
        assert new_data == stock_inflow, f"초기 수량과 동일하지 않음. 초기 수량: {stock_inflow}, 현재 수량: {new_data}"
        page.click("button[data-testid='btn_confirm']")  # 수령 확인 버튼 클릭
        page.wait_for_timeout(2000)
        
        # 수령 상태 확인
        page.locator("data-testid=btn_reset").click()
        page.wait_for_timeout(1000) 
        page.locator("data-testid=input_search").fill(product_name)
        page.wait_for_timeout(1000)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000) 
        
        rows = page.locator("table tbody tr")
        found = False
        for i in range(rows.count()):
            row = rows.nth(i)
            columns = row.locator("td").all_inner_texts()
            if product_name in columns[1]:
                status = columns[0].strip()
                assert status == "수령 완료", f"[FAIL] {product_name} 상태가 '수령 완료'가 아님 → 현재 상태: {status}"
                print(f"[PASS] 수령 완료 상태 확인 완료 → {product_name} 상태: {status}")
                found = True
                break

        if not found:
            raise AssertionError(f"[FAIL] 발주 내역에서 제품 '{product_name}'을 찾을 수 없습니다.")


        # 재고 관리 → 재고 확인
        page.goto(URLS["bay_stock"])
        page.wait_for_timeout(3000)
        page.fill("data-testid=input_search", product_name)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(3000)

        current_stock_text = page.locator("table tbody tr td:nth-child(6)").inner_text()
        current_stock = int(current_stock_text.strip())

        expected_stock = int(previous_stock) + stock_inflow
        assert current_stock == expected_stock, f"[FAIL] 재고 불일치: 예상 {expected_stock}, 실제 {current_stock}"
        print(f"[PASS] 재고 확인 완료 → 예상: {expected_stock}, 실제: {current_stock}")

        # 수령완료 후 발주 예정 내역의 "수령완료"상태 확인
        check_approval_status_buttons(page, "수령 완료", product_name, "자동화규칙_개별", False, False)   


    except Exception as e:
        print(f"❌ Error in test_order_receive_and_inventory_check: {str(e)}")
        raise

# 유틸 함수 
def run_order_status_check(page: Page, delivery_status: int, product_name:str):
    status_name = "수령 완료"
    
    # 상태에 따른 expected 키 매핑
    status_key_map = {
        7: "수령 완료(배송전)", # 제품_3
        4: "수령 완료(배송후)", # 제품_2
    }

    expected_key = status_key_map.get(delivery_status)
    if not expected_key:
        raise ValueError(f"지원하지 않는 delivery_status: {delivery_status}")

    expected = order_status_map[expected_key]

    try:
        
        bay_login(page, "jekwon")

        # 발주 내역 검색
        page.goto(URLS["bay_orderList"])
        search_order_history(page, product_name, status_name)

        # order_id 확인 및 상태 체크
        order_id = get_order_id_from_order_list(page, product_name)
        if not order_id:
            raise ValueError(f"[발주 내역에서 제품 '{product_name}'의 order_id를 찾을 수 없습니다.]")

        check_order_status_by_order_id(page, status_name, order_id, expected)

    except Exception as e:
        print(f"❌ Error in test_order_status_complete: {str(e)}")
        raise


filtered_products = ["자동화개별제품_2", "자동화개별제품_3"] 
alim_talk_product = "수동 발주 제품 3"
# 발주 진행 상태에서 수령 확정 (운송장 X)
def test_order_status_complete_bf(page: Page):
    
    run_order_status_check(page, delivery_status=7, product_name=filtered_products[1])
    
# 배송 진행 상태에서 수령 확정 (운송장 O)
def test_order_status_complete_af(page: Page):
    run_order_status_check(page, delivery_status=4, product_name=filtered_products[0])

# 재발송 버튼 확인
def test_resend_alimtalk(page:Page):
    bay_login(page, "jekwon")
    page.goto(URLS["bay_orderList"])
    page.wait_for_selector("data-testid=input_search", timeout=5000)
    search_order_history(page, alim_talk_product, "발주 요청")

    for i in range(1, 6):  # 1~5회 시도
        page.wait_for_selector("data-testid=btn_resend", timeout=5000)
        page.locator("data-testid=btn_resend").first.click()

        expect(page.locator("data-testid=txt_resend")).to_have_text("재발송하시겠습니까?", timeout=5000)
        page.locator("data-testid=btn_confirm").click()

        if i <= 3:
            # 1~3회차 → 정상 재발송 완료 토스트
            expect(page.locator("data-testid=toast_resend")).to_have_text("재발송이 완료되었습니다.", timeout=5000)
            print(f"✅ {i}회차: 재발송 성공")
        else:
            # 4회차 이후 → 최대 횟수 초과 토스트
            expect(page.locator("data-testid=toast_resend_max")).to_have_text("재발송은 최대 3회까지만 가능합니다.", timeout=5000)
            print(f"⚠️ {i}회차: 재발송 최대 횟수 초과")
