import json
import os

# 테스트 결과 예시 데이터
test_results = [
    {
        "name": "[제품등록] Validation 중복 테스트",
        "file": "tests/Bay_prdctg_val.py",
        "status": "passed"
    },
    {
        "name": "[재고출고] 수량 차감 오류",
        "file": "tests/Bay_stock.py",
        "status": "failed",
        "message": "Expected inventory to decrease by 5",
        "stack": "Traceback (most recent call last): ..."
    }
]

# 결과 파일 저장 위치
output_path = os.path.join("scripts", "summary.json")

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)

print("✅ summary.json 파일 생성 완료:", output_path)
