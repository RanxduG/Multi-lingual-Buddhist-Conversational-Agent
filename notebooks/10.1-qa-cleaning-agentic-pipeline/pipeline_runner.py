from config.langsmith_config import setup_langsmith
setup_langsmith()  # MUST be first — before all other imports

import time
from graph.builder import build_graph
from utils.file_handler import load_input, save_output
from utils.logger import get_logger
from config.settings import (
    INPUT_PATH,
    APPROVED_OUTPUT_PATH,
    REJECTED_OUTPUT_PATH,
    SLEEP_BETWEEN_PAIRS,
)

logger = get_logger(__name__)


def run_pipeline():
    logger.info("Loading raw dataset...")
    raw_pairs = load_input(INPUT_PATH)
    logger.info(f"Loaded {len(raw_pairs)} QA pairs")

    # --- TEST MODE: uncomment to process only first 5 pairs ---
    # raw_pairs = raw_pairs[:5]

    graph = build_graph()
    approved = []
    rejected = []

    for i, pair in enumerate(raw_pairs):
        pair_id = f"pair_{str(i + 1).zfill(4)}"
        logger.info(f"Processing {pair_id} ({i + 1}/{len(raw_pairs)})")

        initial_state = {
            "id": pair_id,
            "question_en": pair["question_en"],
            "question_si": pair["question_si"],
            "original_answer_en": pair["answer_en"],
            "original_answer_si": pair["answer_si"],
            "type": pair.get("type", ""),
            "difficulty": pair.get("difficulty", ""),
            "method": pair.get("method", ""),
            "source": pair.get("source", ""),
            "moderation_passed": False,
            "moderation_reason": None,
            "refined_answer_en": "",
            "english_refinement_attempts": 0,
            "refined_answer_si": "",
            "sinhala_refinement_attempts": 0,
            "quality_passed": False,
            "quality_failure_reason": None,
            "quality_attempts": 0,
            "validation_passed": False,
            "validation_failure_reason": None,
            "validation_attempts": 0,
            "status": "processing",
            "rejection_reason": None,
            "stage_failed_at": None,
        }

        try:
            final_state = graph.invoke(initial_state)

            if final_state["status"] == "approved":
                approved.append(build_approved_record(final_state))
                logger.info(f"  ✓ Approved — {pair_id}")
            else:
                rejected.append(build_rejected_record(final_state))
                logger.info(
                    f"  ✗ Rejected — {pair_id} "
                    f"[{final_state.get('stage_failed_at', 'unknown')}] "
                    f"— {final_state.get('rejection_reason', 'no reason recorded')}"
                )

        except Exception as e:
            logger.error(f"  ERROR processing {pair_id}: {str(e)}")
            rejected.append({
                "id": pair_id,
                "question_en": pair.get("question_en", ""),
                "question_si": pair.get("question_si", ""),
                "answer_en": pair.get("answer_en", ""),
                "answer_si": pair.get("answer_si", ""),
                "status": "error",
                "rejection_reason": f"Unhandled exception: {str(e)}",
                "stage_failed_at": "pipeline_runner",
                "metadata": {
                    "type": pair.get("type", ""),
                    "difficulty": pair.get("difficulty", ""),
                    "method": pair.get("method", ""),
                    "source": pair.get("source", ""),
                },
            })

        time.sleep(SLEEP_BETWEEN_PAIRS)

    save_output(approved, APPROVED_OUTPUT_PATH)
    save_output(rejected, REJECTED_OUTPUT_PATH)

    total = len(raw_pairs)
    logger.info(f"\n{'=' * 50}")
    logger.info(f"  Pipeline complete.")
    logger.info(f"  Total     : {total}")
    logger.info(f"  Approved  : {len(approved)}")
    logger.info(f"  Rejected  : {len(rejected)}")
    if total > 0:
        logger.info(f"  Rate      : {len(approved) / total * 100:.1f}%")
    logger.info(f"{'=' * 50}")


def build_approved_record(state: dict) -> dict:
    return {
        "id": state["id"],
        "english": {
            "question": state["question_en"],
            "answer_original": state["original_answer_en"],
            "answer_refined": state["refined_answer_en"],
        },
        "sinhala": {
            "question": state["question_si"],
            "answer_original": state["original_answer_si"],
            "answer_refined": state["refined_answer_si"],
        },
        "metadata": {
            "type": state["type"],
            "difficulty": state["difficulty"],
            "method": state["method"],
            "source": state["source"],
            "english_refinement_attempts": state["english_refinement_attempts"],
            "sinhala_refinement_attempts": state["sinhala_refinement_attempts"],
            "quality_attempts": state["quality_attempts"],
            "validation_attempts": state["validation_attempts"],
            "moderation_passed": state["moderation_passed"],
            "status": "approved",
        },
    }


def build_rejected_record(state: dict) -> dict:
    return {
        "id": state["id"],
        "question_en": state["question_en"],
        "question_si": state["question_si"],
        "answer_en": state["original_answer_en"],
        "answer_si": state["original_answer_si"],
        "status": "rejected",
        "rejection_reason": state.get("rejection_reason", "unknown"),
        "stage_failed_at": state.get("stage_failed_at", "unknown"),
        "metadata": {
            "type": state["type"],
            "difficulty": state["difficulty"],
            "method": state["method"],
            "source": state["source"],
        },
    }


if __name__ == "__main__":
    run_pipeline()
