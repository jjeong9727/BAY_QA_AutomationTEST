import json
import os

# ✅ 전체 이름 고정 매핑
full_name_mapping = {
    "test_login_success": "로그인 성공",
    "test_login_wrong_password": "잘못된 비밀번호",
    "test_login_empty_fields": "빈 입력값 검증",
    "test_register_product": "단일 제품 등록",
    "test_register_multiple_products": "여러 제품 등록",
    "test_duplicate_product_name": "제품명 중복 등록"
}

# ✅ 단어 매핑
word_mapping = {
    "login": "로그인",
    "wrong": "잘못된",
    "password": "비밀번호",
    "empty": "빈",
    "fields": "입력값",
    "duplicate": "중복",
    "type": "구분",
    "category": "종류",
    "maker": "제조사",
    "add": "추가",
    "register": "등록",
    "bulk": "일괄",
    "delete": "삭제",
    "edit": "수정",
    "product": "제품",
    "products": "제품",
    "stock": "재고",
    "inflow": "입고",
    
}

# ✅ 테스트 파일명 기반 메뉴 매핑
menu_mapping = {
    "test_Bay_login.py": "로그인",
    "test_Bay_delivery.py": "배송",
    "test_Bay_prdctg.py": "카테고리",
    "test_Bay_prdctg_val.py": "카테고리",
    "test_Bay_product.pt": "제품관리",
    "test_Bay_product_delete.py": "제품관리",
    "test_Bay_product_edit.py": "제품관리",
    "test_Bay_product.val.py": "제품관리",
    "test_Bay_stock_in.py": "재고관리_입고",
    "test_Bay_stock_out.py" : "재고관리_출고"
}

# ✅ name 생성 함수
def prettify_name(raw_name: str, file: str, status: str) -> str:
    filename = os.path.basename(file)
    menu = menu_mapping.get(filename, "기타")

    # 1. 고정 매핑 우선
    if raw_name in full_name_mapping:
        label = full_name_mapping[raw_name]
    else:
        words = raw_name.replace("test_", "").split("_")
        pretty_words = [word_mapping.get(w, w) for w in words]
        label = " ".join(pretty_words)

    # 2. 포맷 구성
    name = f"[자동화][{menu}] {label}"
    if status == "failed":
        name += " 테스트 실패"

    return name

# ✅ 요약 파일 생성
def extract_results(report_path="result.json", output_path="scripts/summary.json"):
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    print("✅ result.json 내용 확인:", report)  # 추가된 디버깅

    summary = []

    tests = report.get("report", {}).get("tests", [])
    print("테스트 항목 개수:", len(tests))  # 테스트 항목 개수 확인

    for test in tests:
        print(f"Processing test: {test.get('name')}")  # 현재 처리 중인 테스트 출력

        raw_name = test.get("name", "").split("::")[-1]
        file = test.get("name", "").split("::")[0]
        status = test.get("outcome", "")
        message = ""
        stack = ""

        # 실패한 테스트에 대해 에러 메시지와 스택 트레이스를 추가
        if status == "failed":
            longrepr = test.get("longrepr", "")
            if isinstance(longrepr, dict):
                message = longrepr.get("reprcrash", {}).get("message", "")
                stack = longrepr.get("reprtraceback", {}).get("reprentries", [{}])[-1].get("data", "")
            elif isinstance(longrepr, str):
                message = longrepr
                stack = longrepr

        # 요약에 PASS와 FAIL 모두 추가
        summary.append({
            "name": prettify_name(raw_name, file, status),
            "file": file,
            "status": status,
            "message": message,
            "stack": stack
        })

    # 요약 파일 작성
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("✅ summary.json 생성 완료")

if __name__ == "__main__":
    extract_results()
