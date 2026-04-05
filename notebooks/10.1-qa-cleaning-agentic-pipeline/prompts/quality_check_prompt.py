QUALITY_CHECK_PROMPT = """You are a strict quality evaluator for a bilingual Buddhist knowledge QA dataset.

English Question: {question_en}
Original English Answer: {original_answer_en}
Refined English Answer: {refined_answer_en}

Sinhala Question: {question_si}
Original Sinhala Answer: {original_answer_si}
Refined Sinhala Answer: {refined_answer_si}

Evaluate the refined answers against these criteria:

ENGLISH EVALUATION:
1. en_no_robotic_phrases (bool): Is the refined English answer completely free of AI filler phrases?
2. en_factually_consistent (bool): Does the refined English answer preserve all facts from the original without adding or removing information?
3. en_natural_language (bool): Does the refined English answer sound like a knowledgeable human wrote it?

SINHALA EVALUATION:
4. si_no_robotic_phrases (bool): Is the refined Sinhala answer free of AI filler phrases?
5. si_factually_consistent (bool): Does the refined Sinhala answer preserve all facts from the original Sinhala answer?
6. si_natural_language (bool): Does the refined Sinhala answer read as natural Sinhala that a native speaker would use?

Return a JSON object ONLY in this exact format — no other text, no markdown fences:
{{
  "passes": true or false,
  "en_no_robotic_phrases": true or false,
  "en_factually_consistent": true or false,
  "en_natural_language": true or false,
  "si_no_robotic_phrases": true or false,
  "si_factually_consistent": true or false,
  "si_natural_language": true or false,
  "reason": "Specific description of what failed if passes is false, otherwise empty string"
}}

passes must be true ONLY if ALL six criteria are true."""
