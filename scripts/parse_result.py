import json
import os
import re

# 테스트 이름 한글 매핑
full_name_mapping = {
    "test_Bay_login": "[로그인] 로그인 로그아웃 확인",
    "test_Bay_alert" : "[공통] 화면 이탈 및 검색 확인",
    "test_Bay_supplier": "[업체관리] 업체 등록 및 중복 확인",
    "test_Bay_prdctg": "[카테고리관리] 카테고리 등록 수정 삭제 확인",
    "test_Bay_rule_order":"[발주규칙관리] 발주 규칙 등록 수정 삭제 확인",

    "test_Bay_rule_approval":"[승인규칙관리] 승인 규칙 등록 수정 삭제 확인",
    "test_Bay_product": "[제품관리] 본사 제품 등록 확인",
    "test_Bay_product_upload_validation": "[제품관리] 엑셀 데이터 유효성 검사",
    "test_Bay_product_upload": "[제품관리] 본사 엑셀 업로드 유효성 검사",
    "test_Bay_rule_order_apply_bulk.py": "[발주규칙] 발주 규칙 일괄 적용 확인",

    "test_Bay_product_edit": "[제품관리] 본사 수정, 지점 수정 삭제 복구 확인",
    "test_Bay_stock_in": "[재고관리] 재고 입고 확인",
    "test_Bay_stock_out": "[재고관리] 수동 발주 및 재고 출고 확인",
    "test_Bay_order_pending":"[발주예정내역] 발주 승인 요청 및 예정 내역 수정 삭제",
    "test_Bay_order_approval":"[발주승인요청내역] 승인 거절 확인",

    "test_Bay_order_status_cancel": "[발주내역] 발주 취소, 발주 실패 상태 확인",
    "test_Bay_order_status_request": "[발주내역] 발주 수락 확인",
    "test_Bay_order_status_delivery": "[발주내역] 운송장 등록 확인",
    "test_Bay_order_status_receive": "[발주내역] 발주, 배송 진행 상태에서 수령 확인",
    "test_Bay_order_status_complete": "[발주내역] 수령 완료 상태 확인",
    
    "test_Bay_order_status_batch":"[발주 내역] 통합 내역 확인",
    "test_Bay_stock_history":"[재고관리] 재고 상세 내역 과거 이력 확인",

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

# stack 요약 생성 (에러 유형/메시지 우선 추출)
def summarize_stack(stack: str) -> str:
    if not stack:
        return ""
    lines = stack.strip().splitlines()
    # 1. AssertionError 메시지 추출
    for line in lines:
        if "AssertionError" in line:
            return line.strip()

    # 2. TimeoutError / Locator 관련
    for line in lines:
        if "TimeoutError" in line or "Locator" in line:
            return line.strip()

    # 3. 마지막 줄 (보통 에러 메시지 요약)
    return lines[-1].strip()

def extract_results(input_path="test_results.json", output_path="scripts/summary.json"):
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

    print(f"✅ summary.json 저장 완료 ({len(result)}건)")

if __name__ == "__main__":
    extract_results()