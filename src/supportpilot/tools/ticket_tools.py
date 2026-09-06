from agents import function_tool
from supportpilot.db import (
    create_ticket_in_db,
    get_order_from_db,
    get_ticket_from_db,
    update_ticket_status_in_db,
)


@function_tool
def create_ticket(
    order_id: str,
    issue_type: str,
    description: str,
) -> str:
    """为指定订单创建售后工单。"""

    print(
        f"\n[Tool] 正在创建工单："
        f"order_id={order_id}, "
        f"issue_type={issue_type}"
    )

    order_id = order_id.strip().upper()
    issue_type = issue_type.strip()
    description = description.strip()

    if not order_id:
        return "创建工单失败：订单号不能为空。"

    if not issue_type:
        return "创建工单失败：问题类型不能为空。"

    if not description:
        return "创建工单失败：问题描述不能为空。"

    order = get_order_from_db(order_id)

    if order is None:
        return "创建工单失败：未找到对应订单。"

    ticket_id = create_ticket_in_db(
        order_id=order_id,
        issue_type=issue_type,
        description=description,
    )

    result = (
        f"工单创建成功。"
        f"工单编号：T{ticket_id:04d}。"
    )

    print(f"[Tool] {result}")

    return result


@function_tool
def get_ticket_status(ticket_id: str) -> str:
    """根据工单编号查询售后工单状态。"""

    print(f"\n[Tool] 收到工单查询请求：{ticket_id}")

    ticket_id = ticket_id.strip().upper()

    if not ticket_id:
        return "工单编号不能为空。"

    if not ticket_id.startswith("T"):
        return "工单编号格式不正确，请提供类似 T0001 的工单编号。"

    number_part = ticket_id[1:]

    if not number_part.isdigit():
        return "工单编号格式不正确，请提供类似 T0001 的工单编号。"

    ticket_number = int(number_part)

    ticket = get_ticket_from_db(ticket_number)

    if ticket is None:
        result = "未找到该工单，请检查工单编号是否正确。"
        print(f"[Tool] 查询结果：{result}")
        return result

    display_ticket_id = f"T{ticket['ticket_id']:04d}"

    result = (
        f"工单编号：{display_ticket_id}\n"
        f"订单号：{ticket['order_id']}\n"
        f"问题类型：{ticket['issue_type']}\n"
        f"问题描述：{ticket['description']}\n"
        f"工单状态：{ticket['status']}"
    )

    print(f"[Tool] 查询结果：\n{result}")

    return result


@function_tool
def update_ticket_status(
    ticket_id: str,
    new_status: str,
) -> str:
    """更新售后工单状态。"""

    print(
        f"\n[Tool] 收到工单状态更新请求："
        f"ticket_id={ticket_id}, "
        f"new_status={new_status}"
    )

    ticket_id = ticket_id.strip().upper()
    new_status = new_status.strip()

    if not ticket_id:
        return "更新失败：工单编号不能为空。"

    if not ticket_id.startswith("T"):
        return "更新失败：工单编号格式不正确，请提供类似 T0001 的工单编号。"

    number_part = ticket_id[1:]

    if not number_part.isdigit():
        return "更新失败：工单编号格式不正确，请提供类似 T0001 的工单编号。"

    allowed_statuses = {
        "已创建",
        "处理中",
        "已解决",
    }

    if new_status not in allowed_statuses:
        return (
            "更新失败：不支持该工单状态。"
            "可选状态为：已创建、处理中、已解决。"
        )

    ticket_number = int(number_part)

    ticket = get_ticket_from_db(ticket_number)

    if ticket is None:
        return "更新失败：未找到该工单。"

    updated = update_ticket_status_in_db(
        ticket_id=ticket_number,
        new_status=new_status,
    )

    if not updated:
        return "更新失败：工单状态未发生变化。"

    result = f"工单 {ticket_id} 状态已更新为：{new_status}。"

    print(f"[Tool] {result}")

    return result