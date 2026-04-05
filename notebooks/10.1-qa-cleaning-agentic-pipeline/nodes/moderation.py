import json
from langchain_google_genai import ChatGoogleGenerativeAI
from state.qa_state import QAState
from config import settings
from prompts.moderation_prompt import MODERATION_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def moderation_node(state: QAState) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REFINEMENT_MODEL)

    prompt = MODERATION_PROMPT.format(
        question_en=state["question_en"],
        answer_en=state["original_answer_en"],
        question_si=state["question_si"],
        answer_si=state["original_answer_si"],
    )

    try:
        response = llm.invoke(prompt)
        raw = _strip_json_fences(response.content)
        result = json.loads(raw)

        if result.get("safe", False):
            return {"moderation_passed": True, "moderation_reason": None}
        else:
            reason = result.get("reason", "Content flagged as unsafe")
            logger.warning(f"[{state['id']}] Moderation failed: {reason}")
            return {
                "moderation_passed": False,
                "moderation_reason": reason,
            }

    except json.JSONDecodeError as e:
        msg = "Moderation response could not be parsed"
        logger.error(f"[{state['id']}] {msg}: {e}")
        return {
            "moderation_passed": False,
            "moderation_reason": msg,
        }
    except Exception as e:
        msg = f"Gemini API call failed: {str(e)}"
        logger.error(f"[{state['id']}] Moderation error: {msg}")
        return {
            "moderation_passed": False,
            "moderation_reason": msg,
        }
