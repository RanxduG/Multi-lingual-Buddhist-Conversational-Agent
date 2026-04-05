from state.qa_state import QAState
from config.settings import MAX_QUALITY_ATTEMPTS


def route_after_moderation(state: QAState) -> str:
    return "refine_english" if state["moderation_passed"] else "reject"


def route_after_quality_check(state: QAState) -> str:
    if state["quality_passed"]:
        return "validate_sinhala"
    elif state["quality_attempts"] >= MAX_QUALITY_ATTEMPTS:
        return "reject"
    # Still have retries left — loop back through both refinements
    return "refine_english"


def route_after_validation(state: QAState) -> str:
    # Validation failure always rejects with no retry.
    # By this point both answers passed quality check independently.
    # Semantic inconsistency between languages at this stage indicates
    # a fundamental mismatch in the source data that retrying cannot fix.
    return "approve" if state["validation_passed"] else "reject"
