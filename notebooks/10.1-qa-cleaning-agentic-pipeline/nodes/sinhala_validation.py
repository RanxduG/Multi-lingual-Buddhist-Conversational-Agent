import json
from langchain_google_genai import ChatGoogleGenerativeAI
from state.qa_state import QAState
from config import settings
from prompts.sinhala_validation_prompt import SINHALA_VALIDATION_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def sinhala_validation_node(state: QAState) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GEMINI_JUDGE_MODEL)

    prompt = SINHALA_VALIDATION_PROMPT.format(
        question_en=state["question_en"],
        refined_answer_en=state["refined_answer_en"],
        question_si=state["question_si"],
        refined_answer_si=state["refined_answer_si"],
    )

    attempts = state["validation_attempts"] + 1

    try:
        response = llm.invoke(prompt)
        raw = _strip_json_fences(response.content)
        result = json.loads(raw)

        passed = result.get("passes", False)
        issues = result.get("issues", "") if not passed else None
        logger.info(
            f"[{state['id']}] Sinhala validation attempt {attempts}: {'PASS' if passed else 'FAIL'}"
            + (f" — {issues}" if issues else "")
        )
        return {
            "validation_passed": passed,
            "validation_failure_reason": issues,
            "validation_attempts": attempts,
        }

    except json.JSONDecodeError:
        raw_preview = response.content[:200] if "response" in dir() else "no response"
        reason = f"Response could not be parsed as JSON: {raw_preview}"
        logger.error(f"[{state['id']}] Sinhala validation JSON parse error: {reason}")
        return {
            "validation_passed": False,
            "validation_failure_reason": reason,
            "validation_attempts": attempts,
        }
    except Exception as e:
        reason = f"Gemini API call failed: {str(e)}"
        logger.error(f"[{state['id']}] Sinhala validation error: {reason}")
        return {
            "validation_passed": False,
            "validation_failure_reason": reason,
            "validation_attempts": attempts,
        }
