from langchain_google_genai import ChatGoogleGenerativeAI
from state.qa_state import QAState
from config import settings
from prompts.sinhala_refinement_prompt import SINHALA_REFINEMENT_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


def sinhala_refinement_node(state: QAState) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REFINEMENT_MODEL)

    retry_context = ""
    if state["sinhala_refinement_attempts"] > 0 and state.get("quality_failure_reason"):
        retry_context = (
            f"Previous refinement attempt failed quality check with this reason: "
            f"{state['quality_failure_reason']}. Please specifically address this issue."
        )

    prompt = SINHALA_REFINEMENT_PROMPT.format(
        question_en=state["question_en"],
        question_si=state["question_si"],
        answer_si=state["original_answer_si"],
        refined_answer_en=state["refined_answer_en"],
        retry_context=retry_context,
    )

    attempts = state["sinhala_refinement_attempts"] + 1

    try:
        response = llm.invoke(prompt)
        refined = response.content.strip()
        logger.info(f"[{state['id']}] Sinhala refinement attempt {attempts} complete")
        return {
            "refined_answer_si": refined,
            "sinhala_refinement_attempts": attempts,
        }
    except Exception as e:
        msg = f"Gemini API call failed: {str(e)}"
        logger.error(f"[{state['id']}] Sinhala refinement error: {msg}")
        return {
            "refined_answer_si": state["original_answer_si"],
            "sinhala_refinement_attempts": attempts,
        }
