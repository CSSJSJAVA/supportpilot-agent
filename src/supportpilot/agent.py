from agents import Agent

from supportpilot.config import create_model
from supportpilot.tools.order_tools import get_order_status
from supportpilot.tools.ticket_tools import (
    create_ticket,
    get_ticket_status,
    update_ticket_status,
)


def create_support_agent():
    model = create_model()

    return Agent(
        name="SupportPilot",
        instructions=(
            "你是 SupportPilot，一名企业客服 AI Agent。"
            "请用简洁、专业、友好的方式回答用户问题。"

            "编号规则：A 开头的编号是订单号，例如 A1001；"
            "T 开头的编号是售后工单号，例如 T0001。"

            "看到 A 开头的编号时，不需要向用户确认它是不是订单号。"
            "看到 T 开头的编号时，不需要向用户确认它是不是工单号。"

            "如果用户询问订单信息，并提供了订单号，请调用订单查询工具。"

            "如果用户明确要求创建售后工单，并且已经提供订单号、问题类型和问题描述，"
            "请调用创建工单工具。"
            "如果信息不完整，请先向用户询问缺失的信息。"

            "如果用户询问售后工单状态，并提供了工单编号，请调用工单查询工具。"

            "如果用户明确要求更新工单状态，并提供了工单编号和新状态，"
            "请调用工单状态更新工具。"
            "合法状态只有：已创建、处理中、已解决。"

            "回答订单和工单相关问题时，只能基于工具返回的数据，不要自行编造。"
        ),
        model=model,
        tools=[
            get_order_status,
            create_ticket,
            get_ticket_status,
            update_ticket_status,
        ],
    )