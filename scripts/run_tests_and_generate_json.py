import subprocess

def run_tests_and_generate_summary():
    # 순서대로 실행할 테스트 파일 목록
    test_files = [
        "tests/test_Bay_login.py",
        "tests/test_Bay_supplier.py",
        "tests/test_Bay_supplier_val.py",
        "tests/test_Bay_supplier_delete.py",
        "tests/test_Bay_prdctg.py",
        "tests/test_Bay_prdctg_val.py",
        "tests/test_Bay_prdctg_edit.py",
        "tests/test_Bay_prdctg_delete.py",
        "tests/test_Bay_product.py",
        "tests/test_Bay_product_val.py",
        "tests/test_Bay_product_edit.py",
        "tests/test_Bay_product_delete_val.py",
        "tests/test_Bay_product_delete.py",
        "tests/test_Bay_stock_in.py",
        "tests/test_Bay_stock_out.py",
        "tests/test_Bay_order_status_request_cancel.py",
        "tests/test_Bay_order_status_request.py",
        "tests/test_Bay_order_status_progress_delivery.py",
        "tests/test_Bay_order_status_progress_complete.py",
        "tests/test_Bay_order_status_delivery.py",
        "tests/test_Bay_order_status_complete.py",
        "tests/test_Bay_order_status_fail.py"
    ]
    
    # 각 테스트 파일을 순차적으로 실행
    for test_file in test_files:
        print(f"🚀 {test_file} 테스트 실행 중...")
        result = subprocess.run([
            "pytest",                        # pytest 실행
            test_file,                        # 지정한 테스트 파일만 실행
            "--json-report",                  # JSON 리포트 생성
            "--json-report-file=scripts/result.json"  # 결과를 result.json 파일로 저장
        ])

        if result.returncode == 0:
            print(f"✅ {test_file} 테스트 완료")
        else:
            print(f"❌ {test_file} 테스트 실패")

if __name__ == "__main__":
    run_tests_and_generate_summary()