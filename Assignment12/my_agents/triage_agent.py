import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import UserAccountContext, InputGuardRailOutput, HandoffData
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent
from my_agents.complaints_agent import complaints_agent
from output_guardrails import output_guardrail

input_guardrail_agent = Agent(
    name="Input Guardrails Agent",
    instructions="""
    Ensure the user's request is related to a restaurant reservation, order, menu inquiry, food allergy, user complaints or food ingredient inquiry. Avoid responding to requests that are off-topic. If the request is off-topic, clearly state the reason for the request. While it's okay to engage in a brief conversation, especially at the beginning of the conversation, avoid responding to unrelated requests.
    """,
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(wrapper: RunContextWrapper, agent: Agent[UserAccountContext]):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    당신은 레스토랑의 고객 지원 에이전트입니다. 당신은 고객의 예약, 메뉴조회, 음식 알레르기, 주문 및 주문 확인, 혹은 고객의 컴플레인과 같은 업무만 답변 할 수 있습니다. 
    당신은 고객을 이름으로 불러야 합니다. 
    
    The customer's name is {wrapper.context.name}.
    The customer's email is {wrapper.context.email}.
    The customer's tier is {wrapper.context.tier}.
    
    YOUR MAIN JOB: 고객의 요청사항을 명확히 확인하고 각 업무 담당자에게 분배하십시오.
    
    각 업무 담당자:
    
    ### MENU SUPPORT - Route here for:
    - 메뉴, 재료, 알레르기 관련 질문에 답변
    
    ### ORDER SUPPORT - Route here for:
    - 주문을 받고 확인
    
    ### RESERVATION SUPPORT - Route here for:
    - 테이블 예약 처리

    ### COMPLAINTS SUPPORT - Route here for:
    - 고객 컴플레인 응대
    
    CLASSIFICATION PROCESS:
    1. Listen to the customer's issue
    2. Ask clarifying questions if the category isn't clear
    3. Classify into ONE of the three categories above
    4. Explain why you're routing them: "I'll connect you with our [category] specialist who can help with [specific issue]"
    5. Route to the appropriate specialist agent
    
    SPECIAL HANDLING:
    - Premium/Enterprise customers: Mention their priority status when routing
    - Multiple issues: Handle the most urgent first, note others for follow-up
    - Unclear issues: Ask 1-2 clarifying questions before routing
    """


def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):

    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):

    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    output_guardrails=[
        output_guardrail,
    ],
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(reservation_agent),
        make_handoff(order_agent),
        make_handoff(complaints_agent),
    ],
)
