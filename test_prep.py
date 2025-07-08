import pytest
import random
from playwright.sync_api import Page
from config import URLS, Account
from helpers.common_utils import bay_login

def test_prep_bay (page:Page):
    bay_login(page)

    page.goto(URLS["bay_category"])
    page.wait_for_timeout(1000)

    
    # 구분 등록
    page.click("data-testid=tab_type")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("의약품")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medications")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("의료기기")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medical Devices")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("소모품")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Consumables")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 종류 등록 
    page.click("data-testid=tab_category")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("주사제")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("injection")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("연고")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("ointment")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("보톡스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("botox")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 제조사 등록 
    page.click("data-testid=tab_maker")
    page.wait_for_timeout(1000)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("메디톡스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Medytox")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("루트로닉")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Lutronic")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("휴메딕스")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("Humedix")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_add")
    page.wait_for_timeout(1000)
    page.locator("data-testid=input_kor").last.fill("중복테스트")
    page.wait_for_timeout(500)
    page.locator("data-testid=input_eng").last.fill("DupOne")
    page.wait_for_timeout(500)
    page.click("data-testid=btn_save")
    page.wait_for_timeout(2000)

    # 업체 등록 
    page.goto(URLS["bay_supplier"])
    page.wait_for_timeout(1000)

    page.click("data-testid=btn_orderadd")  # 업체 등록 모달 열기
    page.fill("data-testid=input_sup_name", "자동화업체")  # 업체명 입력
    page.fill("data-testid=input_sup_manager", "권정의")  # 담당자 입력
    page.fill("data-testid=input_sup_contact", "01062754153")  # 연락처 입력
    page.click("data-testid=btn_confirm")  # 완료 버튼 클릭
    page.wait_for_timeout(500)
