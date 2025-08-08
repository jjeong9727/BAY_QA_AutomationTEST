order_status_map = {
    "발주 요청": {
        "resend_enabled": True,
        "tracking_text": "대기중",
        "receive_enabled": False,
        "cancel_enabled": True,
    },
    "발주 진행": {
        "resend_enabled": True,
        "tracking_text": "대기중",
        "receive_enabled": True,
        "cancel_enabled": False,
    },
    "배송 진행": {
        "resend_enabled": True,
        "tracking_enabled": True,
        "receive_enabled": True,
        "cancel_enabled": False,
    },                                                                             
    "일부 수령(배송전)": {
        "resend_enabled": False,
        "tracking_text": "대기중",
        "receive_enabled": True,
        "cancel_enabled": False,
    },                                                                             
    "일부 수령(배송후)": {
        "resend_enabled": False,
        "tracking_enabled": True,
        "receive_enabled": True,
        "cancel_enabled": False,
    },
    # 배송 진행 > 수령 (운송장 등록)
    "수령 완료(배송후)": {
        "resend_enabled": False,
        "tracking_enabled": True,
        "receive_enabled": False,
        "cancel_enabled": False,
    },
    # 발주 진행 > 수령 (운송장 미등록) 
    "수령 완료(배송전)": {
        "resend_enabled" : False,
        "tracking_text": "미입력",
        "receive_enabled": False,
        "cancel_enabled": False,
    },
    "발주 취소": {
        "resend_enabled": False,
        "tracking_text": "대기중",
        "receive_enabled": False,
        "cancel_enabled": False,
    },
    "발주 실패": {
        "resend_enabled": True,
        "tracking_text": "미입력",
        "receive_enabled": False,
        "cancel_enabled": True,
    }
}
