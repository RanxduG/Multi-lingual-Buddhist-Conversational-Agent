from typing import TypedDict, Optional


class QAState(TypedDict):
    # --- Input (never modified after initialisation) ---
    id: str                              # Generated: "pair_0001"
    question_en: str                     # Original English question — never changed
    question_si: str                     # Original Sinhala question — never changed
    original_answer_en: str              # Original English answer — never changed
    original_answer_si: str              # Original Sinhala answer — never changed
    type: str
    difficulty: str
    method: str
    source: str

    # --- Moderation ---
    moderation_passed: bool
    moderation_reason: Optional[str]     # Populated only if failed

    # --- English Refinement ---
    refined_answer_en: str               # Starts as ""
    english_refinement_attempts: int     # Starts at 0

    # --- Sinhala Refinement ---
    refined_answer_si: str               # Starts as ""
    sinhala_refinement_attempts: int     # Starts at 0

    # --- Quality Check (evaluates both refined answers together) ---
    quality_passed: bool
    quality_failure_reason: Optional[str]
    quality_attempts: int                # Total quality check + refinement cycles

    # --- Sinhala Validation ---
    validation_passed: bool
    validation_failure_reason: Optional[str]
    validation_attempts: int             # Starts at 0

    # --- Final ---
    status: str                          # "approved" | "rejected" | "processing"
    rejection_reason: Optional[str]
    stage_failed_at: Optional[str]       # "moderation" | "quality_check" | "sinhala_validation"
