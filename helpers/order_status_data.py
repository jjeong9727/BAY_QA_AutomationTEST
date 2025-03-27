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
        "tracking_button": True,
        "receive_enabled": True,
        "cancel_enabled": False,
    },
    "수령 완료": {
        "resend_enabled": False,
        "tracking_button": True,
        "receive_done_text": "수령 완료",
        "receive_enabled": False,
        "cancel_enabled": False,
    },
    "발주 실패": {
        "resend_enabled": True,
        "tracking_text": "대기중",
        "receive_enabled": False,
        "cancel_enabled": True,
    },
    "발주 취소": {
        "resend_enabled": False,
        "tracking_text": "대기중",
        "receive_enabled": False,
        "cancel_enabled": False,
    },
}
