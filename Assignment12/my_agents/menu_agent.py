from agents import Agent, RunContextWrapper
from models import UserAccountContext


def dynamic_menu_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Menu Management specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Shipping)" if wrapper.context.tier != "basic" else ""}
    
    당신의 역할: 메뉴와 관련된 문의에 대한 답변, 메뉴의 재료나 알레르기 관련된 질문에 답변
    """


menu_agent = Agent(
    name="Menu Management Agent",
    instructions=dynamic_menu_agent_instructions,
)
