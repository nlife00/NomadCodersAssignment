from agents import Agent, RunContextWrapper
from models import UserAccountContext


def dynamic_complaints_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Complaints Management specialist helping {wrapper.context.name}.
    
    당신의 역할: 고객의 컴플레인 담당
    """


complaints_agent = Agent(
    name="Complaints Management Agent",
    instructions=dynamic_complaints_agent_instructions,
)
