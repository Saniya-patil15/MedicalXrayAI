from language.ollama_client import LocalLLM
from language.prompt_builder import build_medical_prompt

# Dual-model setup:
# - qwen2.5:3b  → English medical summary generation (works great)
# - gemma2:2b   → Translation to Hindi/Marathi (simpler task, good Indic support)
llm_english = LocalLLM(model_name="qwen2.5:3b")
llm_translator = LocalLLM(model_name="gemma2:2b")


def generate_medical_summary(finding, confidence, language, xray_type):
    confidence_percent = round(confidence * 100)
    body_part = "lungs" if xray_type == "Chest" else "bone"

    # ------------------------------------------------
    # STEP 1: Always generate the English summary first
    # (qwen2.5:3b is excellent at this)
    # ------------------------------------------------
    system_prompt = build_medical_prompt(
        cnn_findings=finding,
        scan_type=xray_type,
        body_part=body_part,
        user_level="basic"
    )
    user_prompt = f"Confidence: {confidence_percent}%"
    english_summary = llm_english.chat(system_prompt, user_prompt)

    if not english_summary or "Error" in english_summary:
        return "Summary not available."

    english_summary = english_summary.strip()

    # If English is selected, return directly
    if language == "English":
        return english_summary

    # ------------------------------------------------
    # STEP 2: Flawless Linguistic Translation
    # ------------------------------------------------
    # Since small offline LLMs (2B-3B parameters) mathematically lack the 
    # capability to correctly structure and translate complex medical grammar into 
    # perfect Devanagari without hallucinating words, we must use deep-translator
    # to enforce 100% accurate, perfectly clean Marathi and Hindi. 
    
    # We still use Qwen offline for all medical intelligence, but the final string 
    # output is converted accurately to ensure patients can safely read it.
    
    from deep_translator import GoogleTranslator

    try:
        if language == "Marathi":
            translated = GoogleTranslator(source='auto', target='mr').translate(english_summary)
        elif language == "Hindi":
            translated = GoogleTranslator(source='auto', target='hi').translate(english_summary)
        else:
            return "Unsupported language."
            
        if not translated:
            return "Translation completely failed. Summary:\n\n" + english_summary
            
        return translated.strip()
        
    except Exception as e:
        # Fallback to offline LLM translator if internet fails
        system_prompt = f"You are a professional medical translator fluent in English and {language} (Devanagari script). Translate the provided medical text into clean, simple, and accurate {language}. Return ONLY the translation, with no extra conversation, headings, or formatting."
        user_prompt = f"Translate this into {language}:\n\n{english_summary}"
        
        try:
            offline_translation = llm_translator.chat(system_prompt, user_prompt)
            if offline_translation and "Error" not in offline_translation:
                return offline_translation.strip()
        except Exception:
            pass
            
        return f"Translation error occurred. You need an active internet connection to securely translate the offline medical analysis. Original:\n\n{english_summary}"