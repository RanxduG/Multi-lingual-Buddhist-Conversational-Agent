MODERATION_PROMPT = """You are a content safety classifier for a Buddhist knowledge dataset.

Review the following QA pair and determine if it contains harmful content.

Question (English): {question_en}
Answer (English): {answer_en}
Question (Sinhala): {question_si}
Answer (Sinhala): {answer_si}

Classify whether this content is safe to include in an educational dataset.

IMPORTANT CONTEXT: This is a Buddhist scripture dataset. The following content is
expected and must NOT be flagged as harmful:
- References to death, impermanence, suffering (dukkha) — core Buddhist teachings
- Descriptions of violence in historical or Jataka story contexts
- Religious terminology in Pali, Sanskrit, or Sinhala
- Philosophical discussions of desire, attachment, or the nature of existence

Only flag content that is genuinely harmful, such as:
- Content promoting real-world violence or hatred toward people
- Sexual content
- Content that has no educational value and is purely offensive

Return a JSON object ONLY in this exact format — no other text, no markdown fences:
{{
  "safe": true or false,
  "reason": "Brief explanation if safe is false, otherwise empty string"
}}"""
