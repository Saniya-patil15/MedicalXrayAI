import torch
from ultralytics import YOLO
import cv2
import os

def analyze_bone(image_path):
    print(f"--- Analyzing Bone X-ray for Fractures on GPU ---")
    
    # 1. Load the YOLO model
    # Note: 'yolov8n.pt' is a general model. 
    # For a real project, we use a version fine-tuned on the MURA dataset.
    # For now, we will use the Nano version which is extremely fast.
    model = YOLO('yolov8n.pt') 

    # 2. Run the AI
    # It will automatically use your GTX 1650 (device=0)
    results = model.predict(source=image_path, conf=0.25, device=0)

    # 3. Parse the findings
    findings = []
    for r in results:
        for box in r.boxes:
            # Get the label name (e.g., 'fracture')
            label = model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            findings.append({"label": label, "confidence": conf})
            
    return findings

if __name__ == "__main__":
    # Put a bone/fracture X-ray in this folder named 'bone_test.jpg'
    test_image = os.path.join("test_images", "bone_test.jpg")
    
    try:
        if not os.path.exists(test_image):
            print(f"Please add a bone X-ray image at {test_image}")
        else:
            detections = analyze_bone(test_image)
            
            print("\n--- BONE ANALYSIS RESULTS ---")
            if not detections:
                print("Summary: No fractures or abnormalities detected.")
            else:
                for d in detections:
                    print(f"✅ Detected: {d['label']} (Confidence: {d['confidence']:.2f})")
                    
    except Exception as e:
        print(f"Error: {e}")