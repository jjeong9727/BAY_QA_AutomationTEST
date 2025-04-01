import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests_and_generate_summary():
    print("🚀 테스트 실행 시작...")
    result = subprocess.run([
        "pytest",
        "tests/",
        "--json-report",
        "--json-report-file=scripts/summary.json"
    ])

    if result.returncode == 0:
        print("✅ summary.json 파일 생성 완료: scripts/summary.json")
    else:
        print("❌ 테스트 실행 중 실패 발생")

if __name__ == "__main__":
    run_tests_and_generate_summary()
