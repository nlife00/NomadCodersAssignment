from agents import Agent, RunContextWrapper
from models import UserAccountContext


def dynamic_reservation_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Reservation Management specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Shipping)" if wrapper.context.tier != "basic" else ""}
    
    당신의 역할: 테이블 예약 처리
    """


reservation_agent = Agent(
    name="Reservation Management Agent",
    instructions=dynamic_reservation_agent_instructions,
)
