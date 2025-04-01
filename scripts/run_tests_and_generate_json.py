import subprocess

def run_tests_and_generate_summary():
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
