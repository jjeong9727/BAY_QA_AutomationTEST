import pytest
import requests
import random
from playwright.sync_api import Page, expect
from config import URLS, Account
from helpers.common_utils import bay_login

def generate_name(prefix):
    return f"{prefix}{random.randint(1000, 9999)}"

def login_and_go_to_add_page(page: Page):
    try:
        bay_login(page, "admin")
        page.goto(URLS["bay_category"])
        page.wait_for_timeout(2000)
        page.wait_for_url(URLS["bay_category"])
        page.wait_for_timeout(2000)
    except Exception as e:
        error_message = f"Error in login_and_go_to_add_page: {str(e)}"
        raise
def try_duplicate_registration(page: Page, tab_testid: str, name_kr: str, name_en: str):
    try:
        page.click(f"data-testid={tab_testid}")
        page.wait_for_timeout(2000)

        if page.locator("data-testid=btn_confirm").is_visible():
            page.click("data-testid=btn_confirm")
            page.wait_for_timeout(3000)    

        page.click("data-testid=btn_add")
        page.wait_for_timeout(2000)
        page.locator("data-testid=input_kor").last.fill(name_kr)
        page.wait_for_timeout(1000)
        page.locator("data-testid=input_eng").last.fill(name_en)
        page.wait_for_timeout(1000)
        page.click("data-testid=btn_save")
        page.wait_for_timeout(500)
        page.locator("data-testid=alert_duplicate").wait_for(timeout=5000)

        expect(page.locator("data-testid=alert_duplicate")).to_be_visible(timeout=3000)
        print(f"[PASS] 중복 등록 토스트 확인")

        # 사용중인 카테고리 삭제 시도
        name_kr_locator = page.locator(f"input[data-testid='input_kor']").first
        item_to_delete = None
        item_value_to_delete = None
        row_index = -1
        count = name_kr_locator.count()
        for i in reversed(range(count)):
            item_text = name_kr_locator.nth(i).input_value()
            if "중복테스트" in item_text:
                item_to_delete = name_kr_locator.nth(i)
                item_value_to_delete = item_text
                row_index = i
                break

        if item_to_delete:
            delete_buttons = page.locator("button[data-testid='btn_delete']")
            target_button = delete_buttons.nth(row_index)
            target_button.click()
            # expect(page.locator("txt_delete")).to_be_visible(timeout=3000)
            # page.wait_for_timeout(500)
            # page.locator("data-testid=btn_comfirm").click()
            expect(page.locator("alert_using")).to_be_visible(timeout=3000)
            page.wait_for_timeout(1000)

    except Exception as e:
        raise


# ----- 카테고리 등록 확인 -----
def test_register_category_each(page):

    login_and_go_to_add_page(page)
    test_cases = [
        ("tab_type", "input_kor", "input_eng", True),     # 구분
        ("tab_category", "input_kor", "input_eng", True), # 종류
        ("tab_maker", "input_kor", "input_eng", False),   # 제조사
    ]

    for tab, testid_kor, testid_eng, require_eng in test_cases:
        try:
            page.click(f"data-testid={tab}")
            page.wait_for_timeout(1000)
            page.click("data-testid=btn_add")
            page.wait_for_timeout(1000)
            name_kr = generate_name("자동화등록_한글")
            page.locator(f"data-testid={testid_kor}").last.fill(name_kr)
            page.wait_for_timeout(1000)

            if require_eng:
                name_en = generate_name("Auto_ENG")
                page.locator(f"data-testid={testid_eng}").last.fill(name_en)
                page.wait_for_timeout(1000)

            page.click("data-testid=btn_save")
            expect(page.locator("data-testid=alert_register")).to_be_visible(timeout=3000)
            page.wait_for_timeout(3000)

            # 스크롤을 끝까지 내려서 확인
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

            # input_kor 항목 중 name_kr와 동일한 값이 있는지 확인
            input_kor_locator = page.locator(f"input[data-testid={testid_kor}]")
            found = False
            for i in range(input_kor_locator.count()):
                item_value = input_kor_locator.nth(i).input_value()
                if item_value == name_kr:
                    found = True
                    break

            # 결과에 따라 PASS/FAIL 판단
            assert found, f"❌ 등록 항목 미노출: {name_kr}"
            msg = f"[PASS][카테고리] {tab} 등록 후 리스트 노출 확인 성공 ({name_kr})"
            print(msg)
        except Exception as e:
            fail_msg = f"[FAIL][카테고리] {tab} 등록 후 리스트 미노출\n에러: {str(e)}"
            print(fail_msg)
            raise

# ----- 중복 등록 확인 -----
def test_duplicate_category_names(page):
    bay_login(page, "admin")

    page.goto(URLS["bay_category"])
    page.wait_for_url(URLS["bay_category"], timeout=6000)
    page.wait_for_timeout(1500)

    name_kr = "중복테스트"
    name_en1 = "DupOne"
    name_en2 = "DupTwo"

    # 구분
    try_duplicate_registration(page, "tab_type", name_kr, name_en2)
    # 종류
    try_duplicate_registration(page, "tab_category", name_kr, name_en2)

    # 제조사
    try_duplicate_registration(page, "tab_maker", name_kr, name_en2)

# ----- 수정 확인 -----
def test_edit_category_all(page: Page):
    login_and_go_to_add_page(page)

    test_cases = [
        ("tab_type", "input_kor", "input_eng", True, "구분 저장이 완료되었습니다.", "사용 중인 구분명을 수정하시겠습니까?"),
        ("tab_category", "input_kor", "input_eng", True, "종류 저장이 완료되었습니다.", "사용 중인 종류명을 수정하시겠습니까?"),
        ("tab_maker", "input_kor", "input_eng", False, "제조사 저장이 완료되었습니다.", "사용 중인 제조사명을 수정하시겠습니까?"),
    ]

    for tab, testid_kor, testid_eng, require_eng, expected_msg, txt_nosave in test_cases:
        try:
            page.click(f"data-testid={tab}")
            page.wait_for_timeout(2000)

            name_kr_locators = page.locator(f"input[data-testid='{testid_kor}']")
            row_count = name_kr_locators.count()

            item_to_edit = None
            current_value = None

            for i in range(row_count):
                value = name_kr_locators.nth(i).input_value().strip()
                if value.startswith("수정테스트") or value.startswith("[수정] 수정테스트"):
                    item_to_edit = name_kr_locators.nth(i)
                    current_value = value
                    break

            if not item_to_edit:
                pytest.fail(f"⚠️ {tab}: '수정테스트' 또는 '[수정] 수정테스트' 항목을 찾을 수 없습니다.")

            print(f"✅ 현재 값 ({tab}): {current_value}")

            if current_value.startswith("[수정]"):
                new_value = current_value.replace("[수정] ", "", 1)
            else:
                new_value = f"[수정] {current_value}"

            print(f"🔄 변경할 값: {new_value}")

            item_to_edit.fill(new_value)
            page.wait_for_timeout(500)
            page.locator("data-testid=btn_save").click()
            page.wait_for_timeout(500)

            if page.locator("data-testid=txt_nosave").is_visible(timeout=3000):
                expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
                page.locator("data-testid=btn_confirm").click()

            expect(page.locator("data-testid=alert_register")).to_have_text(expected_msg, timeout=5000)

            print(f"🎉 저장 완료 ({tab}): {new_value}")

        except Exception as e:
            print(f"❌ Error in test_edit_category_all ({tab}): {e}")
            raise


# ----- 삭제 확인 -----
def test_delete_category_all(page: Page):
    bay_login(page, "admin")
    page.goto(URLS["bay_category"])
    page.wait_for_selector("data-testid=tab_type", timeout=10000)
    page.wait_for_timeout(2000)

    test_cases = [
        ("tab_type", "input_kor", "input_eng", True),
        ("tab_category", "input_kor", "input_eng", True),
        ("tab_maker", "input_kor", "input_eng", False),
    ]

    for tab, testid_kor, testid_eng, require_eng in test_cases:
        try:
            page.click(f"data-testid={tab}")
            page.wait_for_timeout(2000)

            name_kr_locator = page.locator(f"input[data-testid='{testid_kor}']")
            item_to_delete = None
            item_value_to_delete = None
            row_index = -1

            count = name_kr_locator.count()
            for i in reversed(range(count)):
                item_text = name_kr_locator.nth(i).input_value()
                if item_text.startswith("자동화등록"):
                    item_to_delete = name_kr_locator.nth(i)
                    item_value_to_delete = item_text
                    row_index = i
                    break

            if item_to_delete:
                delete_buttons = page.locator("button[data-testid='btn_delete']")
                target_button = delete_buttons.nth(row_index)
                target_button.wait_for(state="visible")
                target_button.click()
                page.wait_for_timeout(1000)

                confirm_btn = page.locator("data-testid=btn_confirm")
                if confirm_btn.is_visible(timeout=3000):
                    confirm_btn.click()
                    page.wait_for_timeout(2000)
                    print(f"[PASS] 삭제 완료 ({tab}): {item_value_to_delete}")
                else:
                    alert_using = page.locator("data-testid=alert_using")
                    if alert_using.is_visible(timeout=2000):
                        print(f"[INFO] 삭제 불가 ({tab}): 사용 중인 항목 ({item_value_to_delete})")
                    else:
                        raise Exception(f"❌ {tab}: 삭제 확인 버튼과 삭제 불가 알림 둘 다 표시되지 않음")
            else:
                raise Exception(f"❌ {tab}: 삭제 대상 항목을 찾을 수 없습니다.")

        except Exception as e:
            print(f"❌ Error in test_delete_category_all ({tab}): {e}")
            raise
