from config import URLS

def verify_product_update(page, product_names):
    from helpers.product_utils import update_product_flag
    for name in product_names:
        page.goto(URLS["bay_prdList"])
        page.fill("input[placeholder='제품명 검색']", name)
        page.locator("data-testid=btn_search").click()
        page.wait_for_timeout(1000)

        assert page.locator(f"text={name}").is_visible(), f"❌ 제품 관리 페이지에서 수정 확인 실패: {name}"

    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)

    for name in product_names:
        assert page.locator("table tbody td:nth-child(5)", has_text=name).is_visible(), f"❌ 재고 목록에 수정된 제품명 없음: {name}"
        update_product_flag(name, undeletable=True)

    print(f"[PASS] 수정된 {len(product_names)}개 제품 확인 완료")
