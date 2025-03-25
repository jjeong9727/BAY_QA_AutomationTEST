import json

summary = [
    {
        "name": "[제품등록] Validation 중복 테스트",
        "file": "tests/test_product_register.spec.ts",
        "status": "passed"
    },
    {
        "name": "[재고출고] 수량 차감 오류",
        "file": "tests/test_inventory.spec.ts",
        "status": "failed",
        "message": "Expected inventory to decrease by 5",
        "stack": "Traceback (most recent call last): ...",
        "jira_key": "QA-101"
    },
    {
        "name": "[발주신청] 승인자 권한 없음",
        "file": "tests/test_order.spec.ts",
        "status": "failed",
        "message": "UnauthorizedError: User lacks approval role",
        "stack": "Traceback (most recent call last): ..."
    }
]

with open("summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("✅ summary.json 생성 완료")
