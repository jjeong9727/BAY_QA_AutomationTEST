import json
import os
from datetime import datetime
from helpers.order_status_utils import get_daily_count
from config import URLS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_FILE_PATH = os.path.join(BASE_DIR, "..", "product_name.json")

def generate_product_names():
    now = datetime.now()
    cnt = get_daily_count()
    date = now.strftime("%m%d_%H%M")
    count = f"{cnt:02d}"
    prdname_kor = f"등록테스트_{date}_{count}"
    prdname_eng = f"TestProduct_{date}_{count}"
    return prdname_kor, prdname_eng

def append_product_name(
    prdname_kor: str,
    prdname_eng: str,
    manager: str,
    contact: str,
    type_name: str,
    category: str,
    maker: str,
    safety: int = 0,
    auto_order : int =0
):
    
    try:
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append({
        "kor": prdname_kor,
        "eng": prdname_eng,
        "supplier": "자동화 업체명",
        "manager": manager,
        "contact": contact,
        "type": type_name,
        "category": category,
        "maker": maker,
        "safety" : safety,
        "auto_order": auto_order,
        "order_flag" : 0,
        "stock_qty" : 0
    })

    with open(PRODUCT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return prdname_kor, prdname_eng


def get_all_product_names():
    try:
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_latest_product_name():
    all_names = get_all_product_names()
    if not all_names:
        raise ValueError("❌ 저장된 제품명이 없습니다.")
    return all_names[-1]

def remove_product_name_by_kor(kor_name: str):
    data = get_all_product_names()
    updated = [item for item in data if item["kor"] != kor_name]
    with open(PRODUCT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

def is_product_exist(page, product_name: str) -> bool:
    page.goto(URLS["bay_prdList"]) 
    page.fill("input[placeholder='제품명 검색']", product_name)
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        row = rows.nth(i)
        name = row.locator("td:nth-child(5)").inner_text().strip()
        if product_name in name:
            return True
    return False

def sync_product_names_with_server(page):
    product_list = get_all_product_names()
    valid_list = []

    for item in product_list:
        if is_product_exist(page, item["kor"]):
            valid_list.append(item)
        else:
            print(f"[삭제됨] 서버에 없는 제품명 제거: {item['kor']}")
            remove_product_name_by_kor(item["kor"])  # JSON에서 제거

    return valid_list


def update_product_flag(name_kor: str, **flags):
    path = "product_name.json"
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        products = json.load(f)

    for product in products:
        if product.get("kor") == name_kor:
            product.update(flags)
            break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# 저장된 제품명 목록 불러오기
def load_saved_product_names():
    path = "product_name.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_product_update(page, product_names):
    for name in product_names:
        page.goto(URLS["bay_prdList"])
        page.fill("input[placeholder='제품명 검색']", name)
        page.click("data-testid=btn_search")
        page.wait_for_timeout(1000)

        assert page.locator(f"text={name}").is_visible(), f"❌ 제품 관리 페이지에서 수정 확인 실패: {name}"

    page.goto(URLS["bay_stock"])
    page.wait_for_timeout(1000)

    for name in product_names:
        assert page.locator("table tbody td:nth-child(5)", has_text=name).is_visible(), f"❌ 재고 목록에 수정된 제품명 없음: {name}"

    for name in product_names:
        update_product_flag(name, undeletable=True)

    print(f"[PASS] 수정된 {len(product_names)}개 제품 확인 완료")



def get_product_stock(page, product_name):
    from config import URLS
    page.goto(URLS["bay_stock"])
    page.wait_for_url(URLS["bay_stock"], timeout=10000)
    page.fill("input[placeholder='제품명 검색']", product_name)
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    rows = page.locator("table tbody tr")
    for i in range(rows.count()):
        name_cell = rows.nth(i).locator("td:nth-child(5)").inner_text().strip()
        if product_name in name_cell:
            stock_text = rows.nth(i).locator("td:nth-child(3)").inner_text().strip()
            return int(stock_text) if stock_text.isdigit() else 0

    raise Exception(f"❌ 재고관리에서 제품 '{product_name}'을 찾을 수 없음")

def is_duplicate_supplier_from_product_file(manager: str, contact: str) -> bool:
    try:
        with open(PRODUCT_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

    for item in data:
        if (
            item.get("supplier") == "자동화 업체명" and
            item.get("manager") == manager and
            item.get("contact") == contact
        ):
            return True
    return False

def find_supplier_in_paginated_list(page, supplier: str, manager: str, contact: str) -> bool:
    # 검색
    page.fill("input[placeholder='업체명 검색']", supplier)
    page.click("data-testid=btn_search")
    page.wait_for_timeout(1000)

    while True:
        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            row_text = row.inner_text()
            if supplier in row_text and manager in row_text and contact in row_text:
                return True

        # 다음 페이지 버튼 활성화 여부 확인
        next_button = page.locator("button:has-text('다음')")  # 또는 특정 테스트 ID가 있다면 사용
        if next_button.is_enabled():
            next_button.click()
            page.wait_for_timeout(1000)
        else:
            break

    return False
