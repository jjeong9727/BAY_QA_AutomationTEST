import json
import os
import re

# 테스트 이름 한글 매핑
full_name_mapping = {
    "test_Bay_login": "로그인 확인",
    "test_Bay_alert" : "공통 토스트 팝업 및 검색 기능 확인",
    "test_Bay_order_status_request_cancel": "발주 취소 상태 확인",
    "test_Bay_order_status_request": "발주 요청 상태 확인",
    "test_Bay_order_status_progress_delivery": "발주 진행 상태에서 운송장 등록 확인",
    "test_Bay_order_status_progress_complete": "발주 진행 상태에서 수령 확인",
    "test_Bay_order_status_delivery": "배송 진행 상태 확인",
    "test_Bay_order_status_complete": "수령 완료 상태 확인",
    "test_Bay_order_status_fail": "발주 실패 상태 확인",
    "test_Bay_product_delete": "제품 삭제 확인",
    "test_Bay_product_edit": "제품 수정 확인",
    "test_Bay_product_val": "제품 등록 유효성 검사",
    "test_Bay_product": "제품 등록 확인",
    "test_Bay_prdctg_delete": "카테고리 삭제 확인",
    "test_Bay_prdctg": "카테고리 등록 확인",
    "test_Bay_supplier": "업체 등록 확인",
    "test_Bay_supplier_val": "업체 등록 유효성 검사",
    "test_Bay_supplier_delete": "업체 삭제 확인",
    "test_Bay_stock_in": "재고 입고 확인",
    "test_Bay_stock_out": "재고 출고 확인",
    "test_Bay_stock_history":"재고 내역 확인",
}

category_prefix = {
    "login": "로그인",
    "order": "발주관리",
    "category": "카테고리",
    "product": "제품관리",
    "stock": "재고관리",
    "supplier": "업체관리",
}

# 예쁜 이름
def prettify_name(raw_name):
    readable = full_name_mapping.get(raw_name, raw_name)
    match = re.match(r"test_Bay_([a-z]+)", raw_name)
    category_key = match.group(1) if match else "etc"
    category = category_prefix.get(category_key, "기타")
    return f"[자동화][{category}] {readable} 테스트 실패"

# stack 요약 생성
def summarize_stack(stack):
    if not stack:
        return ""
    lines = stack.strip().splitlines()
    file_lines = [line for line in lines if line.strip().startswith("File")]
    last_file_line = file_lines[-1] if file_lines else ""
    last_line = lines[-1] if lines else ""
    return f"{last_file_line.strip()} → {last_line.strip()}"

def extract_results(input_path="test_results.json", output_path="scripts/summary_.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for item in data:
        test_name = item.get("test_name", "")
        status = item.get("status", "")
        message = item.get("message", "")
        stack = item.get("stack", "")

        if status == "FAIL":
            # 에러 메시지 첫 줄
            first_line = message.strip().splitlines()[0] if isinstance(message, str) else message
            stack_summary = summarize_stack(stack)
        else:
            first_line = "테스트 성공"
            stack_summary = ""

        result.append({
            "name": prettify_name(test_name),
            "file": item.get("file", ""),
            "status": status,
            "message": first_line,
            "stack_summary": stack_summary
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ summary_.json 저장 완료 ({len(result)}건)")

if __name__ == "__main__":
    extract_results()
