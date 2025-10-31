# 파일명 한글 매핑
test_name_mapping = {
    "test_Bay_login.py": "[로그인] 로그인 화면 테스트",
        "test_login_wrong_password": "로그인, 로그아웃 확인",

    "test_Bay_alert.py" : "[공통] 화면 이탈, 필터 검색 테스트",
        "test_alert_category": "카테고리 관리 확인",
        "test_alert_product": "제품 관리 확인",
        "test_alert_stock": "재고 관리 확인",
        "test_alert_order_rules": "발주 규칙 관리 확인",
        "test_alert_supplier_page": "업체 전용 알림톡 진입 확인",
        "test_alert_approval_rules": "승인규칙 관리 확인",
        "test_alert_manual_order": "수동 발주 확인",
        "test_alert_order_rule_bulk": "발주 규칙 일괄 적용 확인",

    "test_Bay_supplier.py": "[업체관리][본사] 업체 관리 화면 테스트",
        "test_register_supplier":"업체 등록 확인",
        "test_register_supplier_duplicate":"업체 중복 등록 불가 확인",

    "test_Bay_category.py": "[카테고리관리][본사] 카테고리 화면 테스트",
        "test_register_category_each":"카테고리 등록 확인",
        "test_duplicate_category_names":"카테고리 중복 등록 불가 확인",
        "test_edit_category_all":"카테고리 수정 확인",
        "test_delete_category_all":"카테고리 삭제 확인",

    "test_Bay_rule_order.py":"[발주규칙관리][본사][지점] 발주 규칙 화면 테스트",
        "test_order_rules_register":"본사 발주 규칙 등록 확인",
        "test_order_rules_edit":"본사 발주 규칙 수정 확인",
        "test_order_rule_branch":"지점 발주 규칙 상세 확인",
        "test_order_rules_delete":"본사 발주 규칙 삭제 확인",

    "test_Bay_rule_approval.py":"[승인규칙관리][지점] 승인 규칙 화면 테스트",
        "test_approval_rules_register":"승인 규칙 등록 확인",
        "test_approval_rules_edit":"승인 규칙 수정 확인",
        "test_delete_approval_rule":"승인 규칙 삭제 확인",

    "test_Bay_product.py": "[제품관리][본사] 제품 등록 테스트",
        "test_register_multiple_products":"제품 등록 확인",
        "test_duplicate_product_name":"제품 중복 등록 불가 확인",

    "test_Bay_product_upload_validation.py": "[제품관리][본사] 엑셀 업로드 미리보기 화면 테스트",
        "test_upload_product_validation_first":"미입력 | 중복 제품 | 연락처 형식 | 자동 발주 수량 오류 태그 및 유효성 문구 확인",
        "test_upload_product_validation_second":"텍스트 최대 입력 제한 | 숫자 최대 입력 제한 | 영문, 숫자 필드 오류 태그 및 유효성 문구 확인",
        "test_upload_product_validation_third":"성공 오류 필터 및 유효성 문구 노출 순서 확인",

    "test_Bay_product_upload.py": "[제품관리][본사] 엑셀 업로드 제품 등록 테스트",
        "test_upload_excel_file": "제품 업로드 성공 확인",

    "test_Bay_rule_order_apply_bulk.py": "[발주규칙][본사] 발주 규칙 일괄 적용 화면 테스트",
        "test_apply_rule_order_bulk": "발주 규칙 일괄 적용 후 UI 확인",

    "test_Bay_product_edit.py": "[제품관리][본사][지점] 제품 수정 테스트",
        "test_edit_products":"본사 제품 수정 확인",
        "test_edit_approval_rule":"지점 제품 수정 확인",
        "test_delete_products":"지점 제품 삭제 및 선택 삭제 확인",
        "test_restore_products":"지점 제품 복구 및 선택 복구 확인",

    "test_Bay_stock_in.py": "[재고관리][지점] 재고 입고 테스트",
        "test_stock_inflow":"개별 항목 입고 후 재고 확인",
        "test_inflow_bulk":"여러 항목 입고 후 재고 확인",

    "test_Bay_stock_out.py": "[재고관리][지점] 재고 출고 및 수동 발주 테스트",
        "test_stock_manual_order":"수동 발주 후 내역 확인",
        "test_stock_outflow":"개별 항목 출고 후 내역 확인",
        "test_edit_stocklist_and_auto_order":"재고관리 목록 수정으로 출고 확인",
        "test_outflow_for_batch_order":"여러 항목 출고 후 통합 내역 확인",

    "test_Bay_order_pending.py":"[발주예정내역][지점] 발주 예정 내역 화면 테스트",
        "test_edit_history_bulk":"내역 수정 후 승인 요청 확인",
        "test_check_status_request":"개별 내역 승인 요청 확인",
        "test_check_status_request_bulk":"통합 내역 승인 요청 확인",
        "test_delete_history":"내역 삭제 확인",

    "test_Bay_order_approval.py":"[발주승인요청내역][지점] 승인 요청 내역 화면 테스트",
        "test_approve_order":"승인 URL에서 승인 및 로그인 확인",
        "test_approve_bulk_order":"승인 요청 내역에서 승인 확인",
        "test_reject_order":"승인 요청 내역에서 승인 후 거절 확인",
        "test_reject_bulk_order":"승인 URL에서 거절 및 로그인 확인",

    "test_Bay_order_status.py": "[발주내역][지점] 개별 내역 테스트",
        "test_order_cancel":"발주 취소 후 UI 확인",
        "test_order_status_fail":"발주 실패 UI 확인",
        "test_order_acceptance":"발주 수락 후 UI 확인",
        "test_order_delivery":"운송장 등록 후 운송장 팝업 및 UI 확인",
        "test_order_receive_from_delivery":"배송 진행 상태에서 수령 확인",
        "test_order_receive_from_progress":"발주 진행 상태에서 수령 확인",
        "test_order_status_complete_bf":"운송장 없는 수령 확정 UI 확인",
        "test_order_status_complete_af":"운송장 있는 수령 확정 UI 확인",
        "test_resend_alimtalk":"재발송 및 발송 제한 확인",

    "test_Bay_order_status_batch.py":"[발주 내역][지점] 통합 내역 테스트",
        "test_cancel_batch_history":"개별 취소 및 일괄 취소 확인",
        "test_receive_without_tracking":"발주 수락 후 일부 수령 및 일괄 수령 확인",
        "test_receive_with_tracking":"운송장 등록 후 개별 수령 확인",

    "test_Bay_stock_history.py":"[재고관리][지점] 재고 상세 화면 테스트",
        "test_inflow_past":"과거 날짜 재고 수정 및 내역 확인",
        "test_stock_bulk_edit":"선택 수정 및 내역 확인",
}

# prefix 지정(Jira 이슈 등록)
category_prefix = {
    "login": "로그인",
    "order": "발주관리",
    "category": "카테고리",
    "product": "제품관리",
    "stock": "재고관리",
    "supplier": "업체관리",
}
