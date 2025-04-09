import json
import os
from datetime import datetime

# 결과를 저장할 파일 경로
TEST_RESULTS_FILE = 'test_results.json'

# 테스트 결과 저장 함수
def save_test_result(test_name, message, status="FAIL"):
    # 결과를 저장할 데이터
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 기존 결과 불러오기
    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    # 새로운 결과 추가
    results.append(result_data)

    # 결과 파일에 저장
    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
