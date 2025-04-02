import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# def run_tests_and_generate_summary():
#     print("🚀 테스트 실행 시작...")
#     result = subprocess.run([
#         "pytest",
#         "tests/",
#         "--json-report",
#         "--json-report-file=scripts/summary.json"
#     ])

#     if result.returncode == 0:
#         print("✅ summary.json 파일 생성 완료: scripts/summary.json")
#     else:
#         print("❌ 테스트 실행 중 실패 발생")

# if __name__ == "__main__":
#     run_tests_and_generate_summary()


# 현재 디렉토리에서 legacy 파일만 추출
test_dir = "tests"
legacy_tests = [
    os.path.join(test_dir, f)
    for f in os.listdir(test_dir)
    if f.endswith("_legacy.py")
]

# 실행 명령어 구성
command = ["pytest", *legacy_tests, "--json-report", "--json-report-file=summary.json"]
print("Running tests:", legacy_tests)

subprocess.run(command)
