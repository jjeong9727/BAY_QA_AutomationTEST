
base_url = "https://stg.bay.centurion.ai.kr"
URLS = {
    "bay_login": f"{base_url}/login",
    "bay_home": f"{base_url}/products", 
    "bay_prdList": f"{base_url}/products",
    "bay_prdAdd": f"{base_url}/products/form",
    "bay_prdedit" : f"{base_url}/products/form",
    "bay_stock": f"{base_url}/stocks",
    "bay_stockadd": f"{base_url}/stocks/add",
    "bay_login": f"{base_url}/login",
    "bay_orderList" : f"{base_url}/orders/history",
    "bay_category" : f"{base_url}/categories_management",
    "bay_supplier" : f"{base_url}/providers-management",
    "base_accept_url" : f"{base_url}/m/providers/orders/",
    # "base_accept_url" : f"{base_url}/m/providers/orders/", # 모바일 전용 화면으로 URL에 "/m" 추가 될 가능성 있음 
    "bay_rules" : f"{base_url}/orders/rule-management",
    
    "bay_approval" : f"{base_url}/orders/approve-request",
    "bay_order_pending" : f"{base_url}/orders/pending",
    "bay_approval_rule" : f"{base_url}/orders/approve-rule-management",
    "base_approval_url" : f"{base_url}/m/orders/", # "{base_approval_url}/{id}/confirm"
    "bay_" : f"{base_url}/",

}


Account = {
    # 공통 데이터 
    "testpw": "12341234",
    "wrongid" : "jekwon@medisolveai.com",
    "wrongpw": "0000",

    # 기존 계정
    "testid": "qaje@medisolveai.com", # 권정의 010-6275-4153
    "testid_je": "qaje@medisolveai.com", # 권정의 010-6275-4153
    "testid_sr" :"qasr@medisolveai.com", # 김사라 010-9879-6020
    "testid_sy" :"qasy@medisolveai.com", # 김수연 010-2303-2620
    "testid_stg" : "stg@medisolveai.com", # QA 계정 
    "testid_qa" : "stg@medisolveai.com", # 법인폰 010-8514-8780
    # 본사 계정
    "testid_admin": "admin@medisolveai.com", # admin 운영본부장 010-8514-8780
    
    # 지점 계정
    "testid_je": "jekwon@medisolveai.com", # 권정의 원장 010-6275-4153 
    "testid_emp": "emp@medisolveai.com", # 황우디 대표원장 010-8514-8780 

    
    "": "", # 
}

HEADER_MAP = {
    "구분명": "col_type",
    "구분명(영문)": "col_type_en",
    "종류명": "col_group",
    "종류명(영문)": "col_group_en",
    "제품명": "col_product",
    "제품명(영문)": "col_product_en",
    "제조사명": "col_maker",
    "제조사명(영문)": "col_maker_en",
    "단가": "col_price",
    "안전 재고": "col_safe_qty",
    "자동 발주 수량": "col_order_qty",
    "업체명": "col_supplier",
    "업체 담당자명": "col_manager",
    "업체 담당자 연락처": "col_contact",
}