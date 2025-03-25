import pytest
import datetime
import os


# ✅ 현재 날짜 가져오기 (YYYY-MM-DD 형식)
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# ✅ 리포트 파일 경로 (날짜 포함)
report_file = f"C:/Users/kjeon/Test_Report/Report_{current_date}.html"

# ✅ pytest 실행 명령어
command = f'pytest C:/Users/kjeon/OneDrive/Desktop/QA/자동화/login_test.py --html="{report_file}" --self-contained-html'

# ✅ 실행
os.system(command)

print(f"📄 테스트 리포트 저장됨: {report_file}")