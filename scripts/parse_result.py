import json
import os
import re
from helpers.test_name_mapping import test_name_mapping

# stack 요약 생성 (에러 유형/메시지 우선 추출)
def summarize_stack(stack: str) -> str:
    if not stack:
        return ""
    lines = stack.strip().splitlines()
    for line in lines:
        if "AssertionError" in line:
            return line.strip()
    for line in lines:
        if "TimeoutError" in line or "Locator" in line:
            return line.strip()
    return lines[-1].strip()

def extract_results(input_path="test_results.json", output_path="scripts/summary.json"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for item in data:
        raw_name = item.get("test_name", "") or item.get("file", "")
        status = item.get("status", "")
        message = item.get("message", "")
        stack = item.get("stack", "")

        # 매핑 적용
        display_name = test_name_mapping.get(raw_name, raw_name)

        if status == "FAIL":
            first_line = message.strip().splitlines()[0] if isinstance(message, str) else message
            stack_summary = summarize_stack(stack)
        else:
            first_line = "테스트 성공"
            stack_summary = ""

        result.append({
            "name": display_name,
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