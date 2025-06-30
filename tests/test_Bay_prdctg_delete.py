import pytest
from playwright.sync_api import Page
from config import URLS, Account
from helpers.common_utils import bay_login


@pytest.mark.parametrize("tab,testid_kor,testid_eng,require_eng", [
    ("tab_type", "input_kor", "input_eng", True),     # 구분
    ("tab_category", "input_kor", "input_eng", True), # 종류
    ("tab_maker", "input_kor", "input_eng", False),   # 제조사
])
def test_delete_category_each(page, tab, testid_kor, testid_eng, require_eng):

    try:
        bay_login(page)
        page.goto(URLS)["bay_category"]
        page.wait_for_timeout(200)
        page.click(f"data-testid={tab}")
        page.wait_for_timeout(500)

        name_kr_locator = page.locator(f"input[data-testid='{testid_kor}']")
        item_to_delete = None
        item_value_to_delete = None
        row_index = -1

        # 가장 마지막 자동화등록 항목 찾기
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
            page.wait_for_timeout(500)

            confirm_btn = page.locator("data-testid=btn_confirm")
            if confirm_btn.is_visible(timeout=3000):
                confirm_btn.click()
                page.wait_for_timeout(1000)
                print(f"[PASS] 삭제 완료: {item_value_to_delete}")
            else:
                alert_using = page.locator("data-testid=alert_using")
                if alert_using.is_visible(timeout=2000):
                    print(f"[INFO] 삭제 불가: 사용 중인 항목 ({item_value_to_delete})")
                else:
                    raise Exception("❌ 삭제 확인 버튼과 삭제 불가 알림 둘 다 표시되지 않음")
        else:
            raise Exception("❌ 삭제 대상 항목을 찾을 수 없습니다.")

    except Exception as e:
        raise
