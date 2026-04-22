from language.ollama_client import LocalLLM

# Use same strong model as summary
chat_llm = LocalLLM(model_name="qwen2.5:3b")


def chat_with_report(finding, confidence, summary, question):
    confidence_percent = round(confidence * 100)

    system_prompt = f"""
You are a helpful and friendly medical assistant.

The patient already has an X-ray report.

REPORT DETAILS:
Condition: {finding}
Confidence: {confidence_percent}%

Summary:
{summary}

RULES:
- Explain in very simple language
- Keep answers short and clear
- Do not use difficult medical terms
- Do not scare the patient
- Give practical advice only
- If unsure, suggest consulting a doctor
- Do NOT repeat the full report unless needed
"""

    user_prompt = question

    response = chat_llm.chat(system_prompt, user_prompt)

    if not response or "Error" in response:
        return "Sorry, I couldn't understand. Please try again."

    return response.strip()