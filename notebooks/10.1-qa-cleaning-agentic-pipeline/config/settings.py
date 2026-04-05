# --- Model Selection ---
# Fast, cheap model for high-volume text rewriting tasks
GEMINI_REFINEMENT_MODEL = "gemini-2.5-flash-lite"

# Stronger reasoning model for judgment/evaluation tasks
GEMINI_JUDGE_MODEL = "gemini-2.5-flash"

# --- Retry Limits ---
MAX_QUALITY_ATTEMPTS = 2      # Max refinement + quality check cycles before reject

# --- File Paths ---
INPUT_PATH = "input/raw_dataset.json"
APPROVED_OUTPUT_PATH = "output/approved_dataset.json"
REJECTED_OUTPUT_PATH = "output/rejected_log.json"

# --- LangSmith ---
LANGSMITH_PROJECT = "buddhist-qa-pipeline-stage2"

# --- Rate Limiting ---
# Prevents hitting Gemini free tier rate limits between pairs
SLEEP_BETWEEN_PAIRS = 1  # seconds — increase to 2 if getting 429 errors
