import pytest
import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.product_utils import update_product_name


def generate_name(prefix):
    return f"{prefix}{random.randint(1000, 9999)}"


def login_and_go_to_add_page(page: Page):
    try:
        print("Logging in and going to category page...")
        page.goto(URLS["bay_login"])
        print(f"Filling credentials: {Account['testid']}")
        page.fill("data-testid=input_id", Account["testid"])
        page.fill("data-testid=input_pw", Account["testpw"])
        page.click("data-testid=btn_login")
        print("Waiting for home page...")
        page.wait_for_url(URLS["bay_home"])
        print("Navigating to category page...")
        page.goto(URLS["bay_category"])
        page.wait_for_timeout(3000)
        page.wait_for_url(URLS["bay_category"])
        print("Category page loaded.")
    except Exception as e:
        error_message = f"Error during login and navigation: {str(e)}"
        raise


@pytest.mark.parametrize("tab,testid_kor,testid_eng,require_eng", [
    ("tab_type", "input_kor", "input_eng", True),     # 구분
    ("tab_category", "input_kor", "input_eng", True), # 종류
    ("tab_maker", "input_kor", "input_eng", False),   # 제조사
])
def test_edit_category_each(browser, tab, testid_kor, testid_eng, require_eng):
    page: Page = browser.new_page()
    
    try:
        login_and_go_to_add_page(page)

        print(f"Clicking on tab: {tab}")
        page.click(f"data-testid={tab}")

        page.wait_for_timeout(3000)

        # '자동화등록'으로 시작하는 항목 찾기
        print(f"Searching for items starting with '자동화등록'...")
        name_kr_locator = page.locator(f"input[data-testid='{testid_kor}']")

        item_to_edit = None
        item_value_to_edit = None  # 수정할 항목의 값을 저장할 변수
        for i in range(name_kr_locator.count()):
            item_text = name_kr_locator.nth(i).input_value()
            if item_text.startswith("자동화등록"):
                item_to_edit = name_kr_locator.nth(i)
                item_value_to_edit = item_text  # 항목의 값을 저장
                row_index = i  # 해당 항목이 몇 번째 행인지 저장
                print(f"Found item to edit: {item_value_to_edit} (Row {row_index + 1})")
                break

        if item_to_edit:
            # 기존 값에 "_수정"을 추가하여 새로운 값으로 수정
            new_value = f"{item_value_to_edit}_수정"
            print(f"Editing item value to: {new_value}")
            item_to_edit.fill(new_value)  # 새로운 값으로 수정

            # 수정 후 저장 버튼 클릭
            print("Saving the edited value...")
            save_button = page.locator("data-testid=btn_save")  # 저장 버튼 클릭
            save_button.click()
            page.wait_for_timeout(1500)

            # 수정된 값이 페이지에 제대로 반영되었는지 확인
            print(f"Checking if the edited value '{new_value}' is displayed...")

            # 정확한 항목을 선택하여 값을 확인 (wait_for_selector 추가)
            edited_item = page.locator(f"input[data-testid='{testid_kor}']").nth(row_index)
            edited_item.wait_for(state="visible")  # 항목이 visible 상태일 때까지 대기
            
            assert edited_item.input_value() == new_value, f"❌ 수정된 값이 제대로 반영되지 않았습니다. 기대값: {new_value}, 실제값: {edited_item.input_value()}"

            msg = f"[PASS][카테고리] {tab} 항목 수정 성공 ({new_value})"
            print(msg)
            update_product_name(item_value_to_edit, new_value)
        else:
            error_message = "❌ '자동화등록' 항목을 찾을 수 없습니다."
            print(error_message)

    except Exception as e:
        error_message = f"❌ Error in test_edit_category_each: {str(e)}"
        print(error_message)
        raise
