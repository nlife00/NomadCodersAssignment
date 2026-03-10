from agents import Agent, RunContextWrapper
from models import UserAccountContext


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Order Management specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Shipping)" if wrapper.context.tier != "basic" else ""}
    
    당신의 역할: 음식에 대한 주문을 받거나 주문 상태를 조회, 주문 취소 등을 처리
    """


order_agent = Agent(
    name="Order Management Agent",
    instructions=dynamic_order_agent_instructions,
)
