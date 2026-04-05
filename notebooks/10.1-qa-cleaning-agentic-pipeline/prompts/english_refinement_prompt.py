ENGLISH_REFINEMENT_PROMPT = """You are a dataset quality engineer refining English answers for a Buddhist knowledge QA dataset.

Question: {question_en}
Answer to refine: {answer_en}
{retry_context}
Your task is to rewrite the answer so that it:
1. Removes all robotic or formulaic AI phrases — specifically remove any of: "Certainly!",
   "Great question!", "As an AI language model", "I'd be happy to", "Of course!",
   "Absolutely!", "Sure!", and any similar filler phrases
2. Sounds natural and conversational — like a knowledgeable human explaining something
3. Flows with logical continuity — sentences connect naturally, no abrupt jumps
4. Preserves ALL factual content from the original — do not add, invent, or remove any information
5. Is appropriately concise — no padding, no repetition, no unnecessary filler
6. Maintains appropriate register for a Buddhist knowledge dataset — respectful and clear

Return ONLY the refined answer text. No explanation, no preamble, no quotation marks."""
