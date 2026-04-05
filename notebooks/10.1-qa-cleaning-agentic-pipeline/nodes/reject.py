from state.qa_state import QAState
from utils.logger import get_logger

logger = get_logger(__name__)


def reject_node(state: QAState) -> dict:
    rejection_reason = state.get("rejection_reason")
    stage_failed_at = state.get("stage_failed_at")

    # Derive rejection context from state if not already set
    if not rejection_reason:
        if not state.get("moderation_passed", True):
            rejection_reason = f"Moderation failed: {state.get('moderation_reason', 'unknown reason')}"
            stage_failed_at = "moderation"
        elif not state.get("quality_passed", True):
            rejection_reason = (
                f"Quality check failed after {state.get('quality_attempts', 0)} attempt(s): "
                f"{state.get('quality_failure_reason', 'unknown reason')}"
            )
            stage_failed_at = "quality_check"
        elif not state.get("validation_passed", True):
            rejection_reason = (
                f"Sinhala validation failed: "
                f"{state.get('validation_failure_reason', 'unknown reason')}"
            )
            stage_failed_at = "sinhala_validation"
        else:
            rejection_reason = "Rejected for unknown reason"
            stage_failed_at = "unknown"

    logger.info(f"[{state['id']}] Rejected at '{stage_failed_at}': {rejection_reason}")
    return {
        "status": "rejected",
        "rejection_reason": rejection_reason,
        "stage_failed_at": stage_failed_at or "unknown",
    }
