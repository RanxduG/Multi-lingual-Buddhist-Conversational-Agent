from langchain_google_genai import ChatGoogleGenerativeAI
from state.qa_state import QAState
from config import settings
from prompts.english_refinement_prompt import ENGLISH_REFINEMENT_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


def english_refinement_node(state: QAState) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REFINEMENT_MODEL)

    retry_context = ""
    if state["english_refinement_attempts"] > 0 and state.get("quality_failure_reason"):
        retry_context = (
            f"Previous refinement attempt failed quality check with this reason: "
            f"{state['quality_failure_reason']}. Please specifically address this issue in your refinement."
        )

    prompt = ENGLISH_REFINEMENT_PROMPT.format(
        question_en=state["question_en"],
        answer_en=state["original_answer_en"],
        retry_context=retry_context,
    )

    attempts = state["english_refinement_attempts"] + 1

    try:
        response = llm.invoke(prompt)
        refined = response.content.strip()
        logger.info(f"[{state['id']}] English refinement attempt {attempts} complete")
        return {
            "refined_answer_en": refined,
            "english_refinement_attempts": attempts,
        }
    except Exception as e:
        msg = f"Gemini API call failed: {str(e)}"
        logger.error(f"[{state['id']}] English refinement error: {msg}")
        # Fall back to original so the pipeline can continue; quality check will evaluate it
        return {
            "refined_answer_en": state["original_answer_en"],
            "english_refinement_attempts": attempts,
        }
