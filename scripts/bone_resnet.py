import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

def load_trained_model(model_path):
    # 1. Recreate the exact same architecture used in training
    model = models.resnet50()
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2) 
    
    # 2. Load your custom weights
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(model_path))
    model = model.to(device)
    model.eval()
    return model, device

def analyze_bone_with_custom_model(image_path, model_path):
    print(f"--- Deep Medical Analysis (Custom ResNet) ---")
    
    model, device = load_trained_model(model_path)

    # 3. Same medical preprocessing
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    img = Image.open(image_path).convert('RGB')
    img_t = preprocess(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_t)
        probs = torch.nn.functional.softmax(outputs, dim=1)
    
    # The categories must match the folder names in your data directory
    # Usually: 0 = fractured, 1 = not_fractured (Check your 'data/training' folder order)
    categories = ["Fracture Detected", "Normal / Healthy"] 
    prob, class_idx = torch.max(probs, 1)
    
    return categories[class_idx], prob.item()

if __name__ == "__main__":
    test_image = "test_images/bone_test.jpg"
    model_file = "models/bone_fracture_resnet.pth"
    
    if os.path.exists(test_image):
        diagnosis, confidence = analyze_bone_with_custom_model(test_image, model_file)
        print(f"\n--- AI DIAGNOSIS ---")
        print(f"Result: {diagnosis}")
        print(f"Confidence: {confidence*100:.2f}%")
    else:
        print("Test image not found.")