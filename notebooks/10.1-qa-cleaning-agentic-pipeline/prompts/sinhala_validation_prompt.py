SINHALA_VALIDATION_PROMPT = """You are a bilingual Sinhala-English Buddhist scholar validating the consistency of a QA pair.

English Question: {question_en}
Refined English Answer: {refined_answer_en}

Sinhala Question: {question_si}
Refined Sinhala Answer: {refined_answer_si}

Verify that the Sinhala answer accurately and completely reflects the English answer.

Evaluate on these criteria:
1. meaning_preserved (bool): Does the Sinhala answer convey the same core meaning as the English answer?
2. nothing_missing (bool): Is all key information from the English answer present in the Sinhala answer?
3. nothing_added (bool): Does the Sinhala answer avoid adding information not present in the English answer?
4. terminology_consistent (bool): Are Buddhist/Pali/Sanskrit terms handled consistently between the two versions?

Return a JSON object ONLY in this exact format — no other text, no markdown fences:
{{
  "passes": true or false,
  "meaning_preserved": true or false,
  "nothing_missing": true or false,
  "nothing_added": true or false,
  "terminology_consistent": true or false,
  "issues": "Specific description of inconsistencies if passes is false, otherwise empty string"
}}

passes must be true ONLY if ALL four criteria are true."""
