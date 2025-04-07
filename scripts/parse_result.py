import json
import os
import re

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
    "test_Bay_stock_out.py": "재고관리_출고"
}

import json
import re
from pprint import pprint  # 오류를 추적할 때 유용하게 사용

import re

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

# 예시 테스트에서 사용하기
longrepr = '''Traceback (most recent call last):
  File "tests/test_Bay_login.py", line 20, in test_login_success
    page.wait_for_selector("data-testid=btn_login", state="hidden", timeout=5000)
  File "C:\\path\\to\\playwright\\_impl\\_connection.py", line 528, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
TimeoutError: Timeout 5000ms exceeded'''

message, stack = extract_message_and_stack(longrepr)
print("Message:", message)
print("Stack:", stack)


def extract_results(report_path="result.json", output_path="scripts/summary.json"):
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





# # ✅ 정규 표현식을 사용하여 에러 메시지 및 스택 트레이스 추출
# def extract_message_and_stack(longrepr: str):
#     # 정규 표현식으로 에러 메시지 및 스택 트레이스 추출
#     error_message_pattern = r"(?<=: ).*(?=\nE)"  # "E" 앞에 있는 메시지 추출
#     stack_trace_pattern = r"(playwright.*(?:\n.*)+)"  # Playwright 오류 메시지부터 그 이후 줄까지 추출

#     # 메시지 추출
#     message = re.search(error_message_pattern, longrepr)
#     stack = re.search(stack_trace_pattern, longrepr)

#     if message:
#         message = message.group(0).strip()
#     else:
#         message = "No error message available."

#     if stack:
#         stack = stack.group(0).strip()
#     else:
#         stack = "No stack trace available."

#     return message, stack

# # ✅ name 생성 함수
# def prettify_name(raw_name: str, file: str, status: str) -> str:
#     filename = os.path.basename(file)
#     menu = menu_mapping.get(filename, "기타")

#     # 1. 고정 매핑 우선
#     if raw_name in full_name_mapping:
#         label = full_name_mapping[raw_name]
#     else:
#         words = raw_name.replace("test_", "").split("_")
#         pretty_words = [word_mapping.get(w, w) for w in words]
#         label = " ".join(pretty_words)

#     # 2. 포맷 구성
#     name = f"[자동화][{menu}] {label}"
#     if status == "failed":
#         name += " 테스트 실패"

#     return name

# # ✅ 요약 파일 생성
# def extract_results(report_path="result.json", output_path="scripts/summary.json"):
#     with open(report_path, "r", encoding="utf-8") as f:
#         report = json.load(f)

#     summary = []
#     tests = report.get("report", {}).get("tests", [])

#     for test in tests:
#         raw_name = test.get("name", "").split("::")[-1]
#         file = test.get("name", "").split("::")[0]
#         status = test.get("outcome", "")
#         message = ""
#         stack = ""

#         # 실패한 테스트에 대해 에러 메시지와 스택 트레이스를 추가
#         if status == "failed":
#             longrepr = test.get("longrepr", "")
            
#             # longrepr의 타입과 내용을 출력하여 확인
#             print("longrepr type:", type(longrepr))
#             print("longrepr content:", longrepr)

#             if isinstance(longrepr, str):
#                 # longrepr이 문자열일 경우, 메시지와 스택 트레이스를 정규 표현식으로 추출
#                 message, stack = extract_message_and_stack(longrepr)

#             elif isinstance(longrepr, dict):
#                 # longrepr이 dict일 경우, 메시지와 스택 트레이스를 다르게 처리
#                 print("longrepr is a dict, examining structure...")
#                 print(longrepr)  # longrepr 내용 출력하여 확인
#                 # 예시로 dict에서 필요한 데이터를 추출
#                 message = longrepr.get("message", "No error message available.")
#                 stack = longrepr.get("stack", "No stack trace available.")


#             # 요약에 PASS와 FAIL 모두 추가
#             summary.append({
#                 "name": prettify_name(raw_name, file, status),
#                 "file": file,
#                 "status": status,
#                 "message": message,
#                 "stack": stack
#             })

#     # 요약 파일 작성
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(summary, f, indent=2, ensure_ascii=False)

#     print("✅ summary.json 생성 완료")

# if __name__ == "__main__":
#     extract_results()
