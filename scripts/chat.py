from language.ollama_client import LocalLLM
from deep_translator import GoogleTranslator

# Strong model for English responses
chat_llm = LocalLLM(model_name="qwen2.5:3b")

# Fallback translator model
translator_llm = LocalLLM(model_name="gemma2:2b")


def translate_text(text, language):
    """
    Translate English text to Marathi/Hindi using proven summary logic
    """
    if language == "English":
        return text

    try:
        if language == "Marathi":
            translated = GoogleTranslator(source="auto", target="mr").translate(text)
        elif language == "Hindi":
            translated = GoogleTranslator(source="auto", target="hi").translate(text)
        else:
            return text

        if translated:
            return translated.strip()

    except Exception:
        pass

    # Offline fallback
    try:
        system_prompt = f"""
You are a professional translator.

Translate the following English medical text into clean, simple {language}.

Use natural everyday language.
Return only translated text.
"""
        translated = translator_llm.chat(system_prompt, text)

        if translated and "Error" not in translated:
            return translated.strip()

    except Exception:
        pass

    return text


def chat_with_report(finding, confidence, summary, question, language="English"):
    question_lower = question.lower().strip()
    confidence_percent = round(confidence * 100)

    # ----------------------------------------------------
    # STEP 1: Smart Template Answers (BEST QUALITY)
    # ----------------------------------------------------

    # Seriousness questions
    if any(word in question_lower for word in [
        "serious", "dangerous", "grave",
        "गंभीर", "धोकादायक",
        "गंभीर है", "खतरनाक"
    ]):
        english_answer = f"""
This condition may or may not be serious depending on symptoms and severity.
Your report suggests {finding.lower()}.
Please consult a doctor, especially if symptoms are worsening.
"""

    # Cure / recovery questions
    elif any(word in question_lower for word in [
        "when cure", "recover", "how long", "better",
        "बरे", "ठीक", "कधी बरे",
        "ठीक होगा", "कब ठीक"
    ]):
        english_answer = """
Recovery time depends on the condition and treatment.
Many patients improve with proper care, rest, and medicines.
Please follow your doctor's advice.
"""

    # Doctor questions
    elif any(word in question_lower for word in [
        "doctor", "hospital",
        "डॉक्टर", "रुग्णालय",
        "डॉक्टर", "अस्पताल"
    ]):
        english_answer = """
It is a good idea to consult a doctor for proper evaluation.
Please seek urgent care if breathing trouble, severe pain, or high fever occurs.
"""

    # Advice questions
    elif any(word in question_lower for word in [
        "care", "advice", "what do", "precaution",
        "काळजी", "सल्ला", "काय करू",
        "क्या करूं", "सलाह"
    ]):
        english_answer = """
Take rest, drink enough fluids, and monitor symptoms carefully.
Avoid strain and follow medicines if prescribed.
Consult a doctor if symptoms worsen.
"""

    # ----------------------------------------------------
    # STEP 2: General fallback LLM
    # ----------------------------------------------------
    else:
        system_prompt = f"""
You are a careful and friendly medical assistant.

Patient report:
Condition: {finding}
Confidence: {confidence_percent}%

Summary:
{summary}

RULES:
- Give short answer (max 3 sentences)
- Use simple language
- Do not give definite diagnosis
- Suggest doctor if needed
- Avoid difficult medical words
"""

        english_answer = chat_llm.chat(system_prompt, question)

        if not english_answer or "Error" in english_answer:
            english_answer = """
Please monitor your symptoms and consult a doctor for proper advice.
"""

    english_answer = english_answer.strip()

    # ----------------------------------------------------
    # STEP 3: Translate if needed
    # ----------------------------------------------------
    return translate_text(english_answer, language)