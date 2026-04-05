import json
from langchain_google_genai import ChatGoogleGenerativeAI
from state.qa_state import QAState
from config import settings
from prompts.quality_check_prompt import QUALITY_CHECK_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def quality_check_node(state: QAState) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_JUDGE_MODEL)

    prompt = QUALITY_CHECK_PROMPT.format(
        question_en=state["question_en"],
        original_answer_en=state["original_answer_en"],
        refined_answer_en=state["refined_answer_en"],
        question_si=state["question_si"],
        original_answer_si=state["original_answer_si"],
        refined_answer_si=state["refined_answer_si"],
    )

    attempts = state["quality_attempts"] + 1

    try:
        response = llm.invoke(prompt)
        raw = _strip_json_fences(response.content)
        result = json.loads(raw)

        passed = result.get("passes", False)
        reason = result.get("reason", "") if not passed else None
        logger.info(
            f"[{state['id']}] Quality check attempt {attempts}: {'PASS' if passed else 'FAIL'}"
            + (f" — {reason}" if reason else "")
        )
        return {
            "quality_passed": passed,
            "quality_failure_reason": reason,
            "quality_attempts": attempts,
        }

    except json.JSONDecodeError:
        raw_preview = response.content[:200] if "response" in dir() else "no response"
        reason = f"Response could not be parsed as JSON: {raw_preview}"
        logger.error(f"[{state['id']}] Quality check JSON parse error: {reason}")
        return {
            "quality_passed": False,
            "quality_failure_reason": reason,
            "quality_attempts": attempts,
        }
    except Exception as e:
        reason = f"Gemini API call failed: {str(e)}"
        logger.error(f"[{state['id']}] Quality check error: {reason}")
        return {
            "quality_passed": False,
            "quality_failure_reason": reason,
            "quality_attempts": attempts,
        }
