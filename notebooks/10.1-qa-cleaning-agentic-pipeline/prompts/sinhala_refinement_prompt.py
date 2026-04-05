SINHALA_REFINEMENT_PROMPT = """You are a Sinhala language expert and Buddhist scholar refining Sinhala answers for a knowledge dataset.

English Question (for reference): {question_en}
Sinhala Question: {question_si}
Sinhala Answer to refine: {answer_si}
Refined English Answer (for reference): {refined_answer_en}
{retry_context}
Your task is to rewrite the Sinhala answer so that it:
1. Removes any robotic or formulaic AI phrases in Sinhala
2. Sounds like natural, conversational modern Sinhala — not a literal word-for-word translation
3. Preserves the complete meaning of the original Sinhala answer exactly
4. Stays consistent in meaning with the refined English answer provided above
5. Uses correct Sinhala grammar and natural sentence structure
6. For Pali/Sanskrit Buddhist terms, uses the standard Sinhala transliteration

Return ONLY the refined Sinhala answer text. No explanation, no preamble."""
