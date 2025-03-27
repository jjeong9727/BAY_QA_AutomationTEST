# 발주 진행 상태
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status

def test_order_status_발주진행(browser):
    check_order_status(browser, "발주 진행", order_status_map["발주 진행"])


