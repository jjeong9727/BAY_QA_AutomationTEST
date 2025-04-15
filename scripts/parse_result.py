import json
import os
import re
from pprint import pprint  # 오류를 추적할 때 유용하게 사용


# ✅ 테스트 함수명 기반 매핑
full_name_mapping = {
    
    
    "test_Bay_order_status_request_cancel": "발주 취소 상태 확인",
    "test_Bay_order_status_request": "발주 요청 상태 확인",
    "test_Bay_order_status_progress_delivery": "발주 진행 상태에서 운송장 등록 확인",
    "test_Bay_order_status_progress_complete": "발주 진행 상태에서 수령 확인",
    "test_Bay_order_status_delivery": "배송 진행 상태 확인",
    "test_Bay_order_status_complete": "수령 완료 상태 확인",
    "test_Bay_order_status_fail": "발주 실패 상태 확인",
    "test_Bay_product_delete_val": "제품 삭제 유효성 검사",
    "test_Bay_stock_in": "재고 입고 확인",
    "test_Bay_stock_out": "재고 출고 확인",
    "test_Bay_product_delete": "제품 삭제 확인",
    "test_Bay_product_edit": "제품 수정 확인",
    "test_Bay_product_val" :"제품 등록 유효성 검사",
    "test_Bay_product":"제품 등록 확인",
    "test_Bay_prdctg_delete":"카테고리 삭제 확인",
    "test_Bay_login":"로그인 확인",
    "test_Bay_supplier":"업체 등록 확인",
    "test_Bay_supplier_val":"업체 등록 유효성 검사",
    "test_Bay_supplier_delete":"업체 삭제 확인",
    "test_Bay_prdctg":"카테고리 등록 확인",

    

}

# 카테고리 매핑 추가
category_prefix = {
    "login": "로그인",
    "order": "발주관리",
    "category": "카테고리",
    "product": "제품관리",
    "stock": "재고관리",
    "supplier": "업체관리"
}


def extract_message_and_stack(longrepr):
    # longrepr이 문자열인 경우
    if isinstance(longrepr, str):
        message = ""
        stack = ""

        # 첫 번째 줄을 에러 메시지로 간주 (정규식으로 첫 줄 추출)
        message_match = re.match(r"^(.*?)(?=\n|$)", longrepr)
        if message_match:
            message = message_match.group(0).strip()

        # 'Traceback'부터 시작하는 부분을 스택 트레이스로 간주 (정규식으로 Traceback 부분 추출)
        stack_match = re.search(r"Traceback.*", longrepr, re.DOTALL)
        if stack_match:
            stack = stack_match.group(0).strip()

        return message, stack

    else:
        # longrepr이 dict인 경우, 필드에 맞춰 처리
        return "Unknown error format", ""

def extract_results(report_path="test_results.json", output_path="scripts/summary.json"):
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    summary = []

    # report는 리스트 구조
    if not isinstance(report, list):
        raise ValueError("❌ 예상하지 못한 JSON 구조입니다. 리스트가 아닙니다.")

    for test in report:
        raw_name = test.get("test_name", "")
        status = test.get("status", "")
        message = test.get("message", "")
        stack = ""

        # 에러 메시지 분해 (선택)
        if status.lower() == "fail" and isinstance(message, str):
            message, stack = extract_message_and_stack(message)

        summary.append({
            "name": prettify_name(raw_name, status),
            "file": "",  # file 필드가 없으므로 빈 값으로 유지
            "status": status,
            "message": message,
            "stack": stack
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("✅ summary.json 생성 완료")






def prettify_name(raw_name, status=None):
    # 예쁜 이름 매핑 (없으면 함수명 그대로 사용)
    readable = full_name_mapping.get(raw_name, raw_name)

    # 카테고리 키 추출 (ex: test_stock_outflow → stock)
    match = re.match(r"test_Bay_([a-z]+)", raw_name)
    category_key = match.group(1) if match else "etc"
    category = category_prefix.get(category_key, "기타")

    return f"[자동화][{category}] {readable} 테스트 실패"



if __name__ == "__main__":
    extract_results()


