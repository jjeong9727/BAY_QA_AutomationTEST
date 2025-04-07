import json
import re

# 정규 표현식으로 에러 메시지 및 스택 트레이스를 추출
def extract_message_and_stack(longrepr: str):
    # 오류 메시지 추출: ": " 뒤로부터 "E" 앞까지
    error_message_pattern = r"(?<=: ).*(?=\nE)"
    stack_trace_pattern = r"(playwright.*(?:\n.*)+)"  # Playwright 오류 메시지부터 그 이후 줄까지 추출

    # 메시지 추출
    message = re.search(error_message_pattern, longrepr)
    stack = re.search(stack_trace_pattern, longrepr)

    if message:
        message = message.group(0).strip()
    else:
        message = "No error message available."

    if stack:
        stack = stack.group(0).strip()
    else:
        stack = "No stack trace available."

    return message, stack

# 테스트 결과 출력 함수
def parse_longrepr_and_print(test):
    # longrepr을 가져오기
    longrepr = test.get("longrepr", "")
    
    # 파일명 출력
    file = test.get("file", "Unknown file")
    
    if isinstance(longrepr, str):
        message, stack = extract_message_and_stack(longrepr)
        
        # 파일명과 추출된 오류 메시지 및 스택 트레이스를 출력
        print(f"Test file: {file}")
        print(f"Error message: {message}")
        print(f"Stack trace: {stack}")
        print("-" * 50)

# 테스트 데이터 예시 (file 키 추가)
test_data = {
    "name": "tests/test_Bay_stock_in_legacy.py::test_stock_inflow",
    "file": "tests/test_Bay_stock_in_legacy.py",  # 파일명 추가
    "longrepr": "browser = <Browser type=<BrowserType name=chromium executable_path=C:\\Users\\kjeon\\AppData\\Local\\ms-playwright\\chromium-1155\\chrome-win\\chrome.exe> version=133.0.6943.16>\n\n    def test_stock_inflow(browser):\n        page = browser.new_page()\n>       page.goto(URLS[\"bay_login\"])\n\ntests\\test_Bay_stock_in_legacy.py:9: \n_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n..\\..\\..\\..\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\playwright\\sync_api\\_generated.py:9018: in goto\n    self._sync(\n..\\..\\..\\..\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\playwright\\_impl\\_page.py:551: in goto\n    return await self._main_frame.goto(**locals_to_params(locals()))\n..\\..\\..\\..\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\playwright\\_impl\\_frame.py:145: in goto\n    await self._channel.send(\"goto\", locals_to_params(locals()))\n..\\..\\..\\..\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\playwright\\_impl\\_connection.py:61: in send\n    return await self._connection.wrap_api_call(\n_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n\nself = <playwright._impl._connection.Connection object at 0x0000029893BBB770>, cb = <function Channel.send.<locals>.<lambda> at 0x0000029893C86340>\nis_internal = False\n\n    async def wrap_api_call(\n        self, cb: Callable[[], Any], is_internal: bool = False\n    ) -> Any:\n        if self._api_zone.get():\n            return await cb()\n        task = asyncio.current_task(self._loop)\n        st: List[inspect.FrameInfo] = getattr(task, \"__pw_stack__\", inspect.stack())\n        parsed_st = _extract_stack_trace_information_from_stack(st, is_internal)\n        self._api_zone.set(parsed_st)\n        try:\n            return await cb()\n        except Exception as error:\n>           raise rewrite_error(error, f\"{parsed_st['apiName']}: {error}\") from None\nE           playwright._impl._errors.TargetClosedError: Page.goto: Target page, context or browser has been closed\nE           Call log:\nE             - navigating to \"http://192.168.0.10:5174/login\", waiting until \"load\"\n\n..\\..\\..\\..\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\playwright\\_impl\\_connection.py:528: TargetClosedError"
}

# 테스트 결과 출력
parse_longrepr_and_print(test_data)
