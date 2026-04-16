from scripts.bone_resnet import analyze_bone_with_custom_model
from scripts.summarizer import generate_medical_summary
import os

# CONFIGURATION
TEST_IMAGE = "test_images/bone_test.jpg"
MODEL_PATH = "models/bone_fracture_resnet.pth"
LANGUAGE = "Marathi" # You can change this to "English" or "Hindi"

def run_full_diagnosis():
    if not os.path.exists(TEST_IMAGE):
        print(f"Error: Could not find {TEST_IMAGE}")
        return

    # 1. RUN VISION ANALYSIS
    print("Step 1: Analyzing X-ray image...")
    finding, confidence = analyze_bone_with_custom_model(TEST_IMAGE, MODEL_PATH)
    print(f"Vision Result: {finding} ({confidence*100:.1f}%)")

    # 2. RUN OLLAMA SUMMARIZER
    print(f"\nStep 2: Requesting {LANGUAGE} summary from Ollama...")
    summary = generate_medical_summary(finding, confidence, language=LANGUAGE)
    
    # 3. FINAL OUTPUT
    print("\n" + "="*30)
    print(f"PATIENT REPORT ({LANGUAGE})")
    print("="*30)
    print(summary)
    print("="*30)

if __name__ == "__main__":
    run_full_diagnosis()