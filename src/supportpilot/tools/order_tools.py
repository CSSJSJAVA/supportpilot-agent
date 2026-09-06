from agents import function_tool

from supportpilot.db import get_order_from_db


@function_tool
def get_order_status(order_id: str) -> str:
    """根据订单号查询订单详情。"""

    print(f"\n[Tool] 收到订单查询请求：{order_id}")

    order_id = order_id.strip().upper()

    if not order_id:
        return "订单号不能为空。"

    if not order_id.startswith("A"):
        return "订单号格式不正确，请提供类似 A1001 的订单号。"

    order = get_order_from_db(order_id)

    if order is None:
        result = "未找到该订单，请检查订单号是否正确。"
        print(f"[Tool] 查询结果：{result}")
        return result

    result = (
        f"订单号：{order['order_id']}\n"
        f"客户：{order['customer_name']}\n"
        f"商品：{order['product_name']}\n"
        f"支付状态：{order['payment_status']}\n"
        f"物流状态：{order['shipping_status']}\n"
        f"预计送达：{order['estimated_delivery']}"
    )

    print(f"[Tool] 查询结果：\n{result}")

    return result