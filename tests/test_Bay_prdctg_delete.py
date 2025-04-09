import pytest
import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.save_test_result import save_test_result 


def login_and_go_to_add_page(page: Page):
    try:
        page.goto(URLS["bay_login"])
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        page.wait_for_url(URLS["bay_home"])
        page.goto(URLS["bay_category"])
        page.wait_for_url(URLS["bay_category"])
        page.wait_for_timeout(1500)
    except Exception as e:
        error_message = f"Error during login and navigation: {str(e)}"
        save_test_result("login_and_go_to_add_page", error_message, status="ERROR")
        raise

@pytest.mark.parametrize("tab,testid_kor,testid_eng,require_eng", [
    ("tab_type", "input_kor", "input_eng", True),     # 구분
    ("tab_category", "input_kor", "input_eng", True), # 종류
    ("tab_maker", "input_kor", "input_eng", False),   # 제조사
])
def test_delete_category_each(browser, tab, testid_kor, testid_eng, require_eng):
    page: Page = browser.new_page()
    
    try:
        login_and_go_to_add_page(page)

        page.click(f"data-testid={tab}")
        page.wait_for_timeout(500)

        # '자동화등록'으로 시작하는 항목 찾기
        name_kr_locator = page.locator(f"input[data-testid='{testid_kor}']")

        item_to_delete = None
        item_value_to_delete = None  # 삭제할 항목의 값을 저장할 변수
        for i in range(name_kr_locator.count()):
            item_text = name_kr_locator.nth(i).input_value()
            if item_text.startswith("자동화등록"):
                item_to_delete = name_kr_locator.nth(i)
                item_value_to_delete = item_text  # 항목의 값을 저장
                row_index = i  # 해당 항목이 몇 번째 행인지 저장
                break

        if item_to_delete:
            # 해당 항목의 행 번호(row_index)를 확인하고, 삭제 버튼 클릭
            delete_button = page.locator(f"div:nth-of-type({row_index + 1}) button[data-testid='btn_delete']")
            
            delete_button.wait_for(state="visible")  # 버튼이 visible 될 때까지 대기
            delete_button.click()  # 삭제 버튼 클릭

            page.locator("data-testid=btn_confirm").click()  # 삭제 확인 버튼 클릭
            page.wait_for_timeout(1500)

            assert not page.locator(f"text={item_value_to_delete}").is_visible(), f"❌ 삭제 후 항목이 여전히 존재: {item_value_to_delete}"

            msg = f"[PASS][카테고리] {tab} 항목 삭제 성공 ({item_value_to_delete})"
            print(msg)
            save_test_result("test_delete_category_each", msg, status="PASS")
        else:
            error_message = "❌ '자동화등록' 항목을 찾을 수 없습니다."
            print(error_message)
            save_test_result("test_delete_category_each", error_message, status="FAIL")

    except Exception as e:
        error_message = f"❌ Error in test_delete_category_each: {str(e)}"
        print(error_message)
        save_test_result("test_delete_category_each", error_message, status="FAIL")
        raise
