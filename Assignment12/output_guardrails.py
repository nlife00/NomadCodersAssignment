from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from models import OutputGuardRailOutput, UserAccountContext

output_guardrail_agent = Agent(
    name="Output Guardrail",
    instructions="""
    모든 에이전트들의 답변을 분석하고 레스토랑의 고객 지원 에이전트로 적합하지 않은 답변인지를 확인합니다. 

    레스토랑과 관련된 문의에만 대답하며 답변이 적절한 경우에만 true를 리턴합니다. 
    """,
    output_type=OutputGuardRailOutput,
)


@output_guardrail
async def output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        output_guardrail_agent,
        output,
        context=wrapper.context,
    )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )
