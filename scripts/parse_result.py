import json
import os
import re
from pprint import pprint  # 오류를 추적할 때 유용하게 사용


# ✅ 테스트 함수명 기반 매핑
full_name_mapping = {
    "test_login_success" : "로그인 성공",
    "test_login_wrong_password" : "로그인 비밀번호 오류",
    "test_order_status_cancel" : "발주 취소 상태 확인",
    "test_order_status_complete" : "발주 완료 상태 확인",
    "test_order_receive_from_delivery" : "배송 상태에서 수령 확인",
    "test_order_status_fail" : "발주 실패 상태 확인",
    "test_order_receive_from_progress" : "진행 중 상태에서 수령 확인",
    "test_order_delivery" : "배송 상태 확인",
    "test_order_cancel" : "발주 취소 상태 확인",
    "test_order_acceptance" : "발주 수락 확인",
    "test_delete_category_each" : "카테고리 삭제 확인",
    "test_edit_category_each" : "카테고리 수정 확인",
    "test_duplicate_category_names" : "카테고리 중복 등록 확인",
    "test_register_category_each" : "카테고리 등록 확인",
    "test_delete_product_validation" : "제품 삭제 유효성 검사",
    "test_delete_product" : "제품 삭제 확인",
    "test_bulk_delete_products" : "제품 일괄 삭제 확인",
    "test_edit_single_product" : "단일 제품 수정 확인",
    "test_edit_bulk_products" : "제품 일괄 수정 확인",
    "test_duplicate_product_name" : "제품명 중복 확인",
    "test_register_product" : "제품 등록 확인",
    "test_register_multiple_products" : "제품 일괄 등록 확인",
    "test_stock_inflow" : "재고 입고 확인",
    "test_stock_outflow" : "재고 출고 확인",
    "test_delete_supplier" : "업체 삭제 확인",
    "test_register_supplier_duplicate" : "업체 중복 확인",
    "test_register_supplier" : "업체 등록 확인"
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
    tests = report.get("report", {}).get("tests", [])

    for test in tests:
        raw_name = test.get("name", "").split("::")[-1]
        file = test.get("name", "").split("::")[0]
        status = test.get("outcome", "")
        message = ""
        stack = ""

        # 실패한 테스트에 대해 에러 메시지와 스택 트레이스를 추가
        if status == "failed":
            longrepr = test.get("longrepr", "")
            
            if isinstance(longrepr, str):
                message, stack = extract_message_and_stack(longrepr)

            summary.append({
                "name": prettify_name(raw_name, file, status),
                "file": file,
                "status": status,
                "message": message,
                "stack": stack
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("✅ summary.json 생성 완료")


def prettify_name(raw_name, file, status):
    """테스트 이름을 예쁘게 포맷팅하는 함수"""
    return f"{file}::{raw_name} - {status}"

if __name__ == "__main__":
    extract_results()


