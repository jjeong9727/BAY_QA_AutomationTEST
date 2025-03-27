# 배송진행 상태
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status

def test_order_status_배송진행(browser):
    check_order_status(browser, "배송 진행", order_status_map["배송 진행"])

