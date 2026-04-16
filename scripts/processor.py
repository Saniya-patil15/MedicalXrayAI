import torch
import torchxrayvision as xrv
import skimage.io
import torchvision.transforms as transforms
import numpy as np
import os


def analyze_chest(image_path):
    # ------------------------
    # 0. Check file
    # ------------------------
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")

    # ------------------------
    # 1. Load image
    # ------------------------
    img = skimage.io.imread(image_path)

    # Normalize to [0,1]
    img = xrv.datasets.normalize(img, 255)

    # Convert to single channel
    if len(img.shape) > 2:
        img = img[:, :, 0]

    # Add channel dimension
    img = img[None, :, :]

    # ------------------------
    # 2. Transform
    # ------------------------
    transform = transforms.Compose([
        xrv.datasets.XRayCenterCrop(),
        xrv.datasets.XRayResizer(224)
    ])

    img = transform(img)
    img = torch.from_numpy(img).float()

    # ------------------------
    # 3. Load model
    # ------------------------
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    model.eval()

    if torch.cuda.is_available():
        model = model.cuda()
        img = img.cuda()

    # ------------------------
    # 4. Inference
    # ------------------------
    with torch.no_grad():
        outputs = model(img)[0].cpu().numpy()

    findings = dict(zip(model.pathologies, outputs))

    # ------------------------
    # 5. SMART MEDICAL GROUPING
    # ------------------------

    pneumonia_group = ["Infiltration", "Consolidation", "Lung Opacity"]
    serious_group = ["Pneumothorax", "Effusion"]

    pneumonia_score = max([findings.get(d, 0) for d in pneumonia_group])
    serious_score = max([findings.get(d, 0) for d in serious_group])

    top_disease = max(findings, key=findings.get)
    top_score = findings[top_disease]

    # ------------------------
    # 6. DECISION LOGIC
    # ------------------------

    # 🚨 Serious condition (high priority)
    if serious_score > 0.6:
        return {
            "prediction": top_disease,
            "confidence": float(serious_score)
        }

    # 🫁 Pneumonia detection (group-based)
    if pneumonia_score > 0.65:
        return {
            "prediction": "Pneumonia / Lung Infection",
            "confidence": float(pneumonia_score)
        }

    # ⚠️ Weak pneumonia signals → NORMAL
    if 0.4 < pneumonia_score <= 0.65:
        return {
            "prediction": "NORMAL",
            "confidence": float(1 - pneumonia_score)
        }

    # ✅ All low → NORMAL
    if top_score < 0.5:
        return {
            "prediction": "NORMAL",
            "confidence": float(1 - top_score)
        }

    # 🔁 Fallback (rare cases)
    return {
        "prediction": top_disease,
        "confidence": float(top_score)
    }