import pytest
from playwright.sync_api import Page, expect
from config import URLS
from helpers.common_utils import bay_login


def login_and_go_to_add_page(page: Page):
    bay_login(page)
    page.goto(URLS["bay_category"])
    page.wait_for_timeout(3000)
    page.wait_for_url(URLS["bay_category"])


@pytest.mark.parametrize("tab,testid_kor,testid_eng,require_eng,expected_msg,txt_nosave", [
    ("tab_type", "input_kor", "input_eng", True, "구분 저장이 완료되었습니다.", "사용 중인 구분명을 수정하시겠습니까?"),
    ("tab_category", "input_kor", "input_eng", True, "종류 저장이 완료되었습니다.", "사용 중인 종류명을 수정하시겠습니까?"),
    ("tab_maker", "input_kor", "input_eng", False, "제조사 저장이 완료되었습니다.", "사용 중인 제조사명을 수정하시겠습니까?"),
])
def test_edit_category_each(page, tab, testid_kor, testid_eng, require_eng, expected_msg, txt_nosave):
    try:
        # 카테고리 관리 페이지 진입
        login_and_go_to_add_page(page)
        page.click(f"data-testid={tab}")
        page.wait_for_timeout(2000)

        # 해당 탭의 모든 한국어 입력란 가져오기
        name_kr_locators = page.locator(f"input[data-testid='{testid_kor}']")
        row_count = name_kr_locators.count()

        item_to_edit = None
        current_value = None

        # '중복테스트' 또는 '[수정] 중복테스트' 항목 찾기
        for i in range(row_count):
            value = name_kr_locators.nth(i).input_value().strip()
            if value.startswith("중복테스트") or value.startswith("[수정] 중복테스트"):
                item_to_edit = name_kr_locators.nth(i)
                current_value = value
                break

        if not item_to_edit:
            pytest.fail("⚠️ '중복테스트' 또는 '[수정] 중복테스트' 항목을 찾을 수 없습니다.")

        print(f"✅ 현재 값: {current_value}")

        # 현재 값 확인 후 토글 값 결정
        if current_value.startswith("[수정]"):
            new_value = current_value.replace("[수정] ", "", 1)
        else:
            new_value = f"[수정] {current_value}"

        print(f"🔄 변경할 값: {new_value}")

        # 입력 후 저장
        item_to_edit.fill(new_value)
        page.wait_for_timeout(500)
        page.locator("body").click(position={"x": 0, "y": 0})
        page.wait_for_timeout(500)
        page.locator("data-testid=btn_save").click()
        page.wait_for_timeout(500)
        
        # 중간 팝업 처리 (사용 중인 항목 수정 여부)
        if page.locator("data-testid=txt_nosave").is_visible(timeout=3000):
            expect(page.locator("data-testid=txt_nosave")).to_have_text(txt_nosave, timeout=3000)
            page.locator("data-testid=btn_confirm").click()

        # 저장 완료 토스트 검증
        expect(page.locator("data-testid=alert_register")).to_have_text(expected_msg, timeout=5000)

        print(f"🎉 저장 완료: {new_value}")

    except Exception as e:
        print(f"❌ Error in test_edit_category_each ({tab}): {e}")
        raise
