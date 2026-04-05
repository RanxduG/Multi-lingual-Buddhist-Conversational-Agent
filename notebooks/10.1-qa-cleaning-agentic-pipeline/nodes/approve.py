from state.qa_state import QAState
from utils.logger import get_logger

logger = get_logger(__name__)


def approve_node(state: QAState) -> dict:
    logger.info(f"[{state['id']}] Approved")
    return {"status": "approved"}
