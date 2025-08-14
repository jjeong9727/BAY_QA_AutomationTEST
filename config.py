
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
    "base_accept_url" : f"{base_url}/providers/orders/",
    # "base_accept_url" : f"{base_url}/m/providers/orders/", # 모바일 전용 화면으로 URL에 "/m" 추가 될 가능성 있음 
    "bay_rules" : f"{base_url}/orders/rule-management",
    
    "bay_approval" : f"{base_url}/",
    "bay_order_pending" : f"{base_url}/",
    "bay_approval_rule" : f"{base_url}/",
    "base_approval_url" : f"{base_url}/m/orders/", # "{base_approval_url}/{id}/confirm"
    "bay_" : f"{base_url}/",

}


Account = {
    "testid_je": "qaje@medisolveai.com", # 권정의 010-6275-4153
    "testid_sr" :"qaje@medisolveai.com", # 김사라 010-9879-6020
    "testid_sy" :"qasy@medisolveai.com", # 김수연 010-2303-2620
    "testid_stg" : "stg@medisolveai.com", # QA 계정 
    "testid_qa" : "stg@medisolveai.com", # QA 계정(법인폰) 010-8514-8780
    "testpw": "12341234",
    "wrongpw": "0000"
}
