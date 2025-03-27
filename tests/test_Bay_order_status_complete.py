# 수령 완료 상태
from helpers.order_status_data import order_status_map
from helpers.order_status_utils import check_order_status

def test_order_status_수령완료(browser):
    check_order_status(browser, "수령 완료", order_status_map["수령 완료"])

