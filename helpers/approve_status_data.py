approve_status_map = {
    # 발주 예정 내역
    "자동 승인": {   
        "status_text": "자동 승인",
        "status_enabled": False,
        "edit_enabled": True,
        "delete_enabled": True, 
    },
    # 발주 예정 내역
    "승인 요청": {   
        "status_text": "승인 요청",
        "status_enabled": True,
        "edit_enabled": True,
        "delete_enabled": True,
    },
    # 발주 예정 내역                                                               
    "승인 완료": {   
        "status_text": "승인 완료",
        "status_enabled": False,
        "edit_enabled": False,
        "delete_enabled": False,
    },           
    # 발주 예정 내역                                                                  
    "승인 거절": {   
        "status_text": "승인 거절",
        "status_enabled": False,
        "edit_enabled": False,
        "delete_enabled": False,
    },
    # 발주 예정 내역
    "수령 완료": {   
        "status_text": "수령 완료",
        "status_enabled": False,
        "edit_enabled": False,
        "delete_enabled": False,
    },
    # 공통
    "승인 대기": {   
        "status_text": "승인 대기", # 공통
        "status_enabled": False, # 발주 예정 내역
        "edit_enabled": False, # 발주 예정 내역
        "delete_enabled": False, # 발주 예정 내역
        "approve_enabled": True, # 승인 요청 내역
        "reject_enabled": True, # 승인 요청 내역
    },    
    # 승인 요청 내역
    "발주 승인":{  
        "status_text": "발주 승인",
        "approve_enabled": False,
        "reject_enabled": False
    },
    # 승인 요청 내역
    "발주 거절":{  
        "status_text": "발주 거절",
        "approve_enabled": False,
        "reject_enabled": False
    }
}
