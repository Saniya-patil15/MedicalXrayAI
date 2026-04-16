import torch
import torchxrayvision as xrv

print("--- GPU Status Check ---")
available = torch.cuda.is_available()
print(f"Is CUDA available? {available}")

if available:
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"VRAM Available: {torch.cuda.get_total_memory(0) / 1024**3:.2f} GB")
    
    # Check if a model can be moved to GPU
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    try:
        model.cuda()
        print("Success: Medical models can run on your GTX 1650!")
    except Exception as e:
        print(f"Error moving model to GPU: {e}")
else:
    print("Action Needed: PyTorch is using CPU. Check your installation command.")