import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os

def train_model():
    # 1. Setup Paths
    data_dir = 'data'
    train_dir = os.path.join(data_dir, 'training')
    val_dir = os.path.join(data_dir, 'testing')
    
    # 2. Data Transformations (Standard for ResNet)
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.RandomHorizontalFlip(), # Augmentation for better learning
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 3. Load Datasets
    image_datasets = {
        'train': datasets.ImageFolder(train_dir, data_transforms['train']),
        'val': datasets.ImageFolder(val_dir, data_transforms['val'])
    }
    
    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=16, shuffle=True),
        'val': DataLoader(image_datasets['val'], batch_size=16, shuffle=False)
    }

    # 4. Initialize ResNet50 and modify for 2 classes
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(weights='DEFAULT')
    
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2) # 2 classes: fractured and not_fractured
    model = model.to(device)

    # 5. Define Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    # 6. Training Loop (Simple version)
    print(f"Starting Training on {str(device).upper()}...")
    num_epochs = 5 # Start with 5 epochs to see progress
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in dataloaders['train']:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
        epoch_loss = running_loss / len(image_datasets['train'])
        print(f"Epoch {epoch+1}/{num_epochs} - Loss: {epoch_loss:.4f}")

    # 7. Save the trained weights
    os.makedirs('models', exist_ok=True)
    torch.save(model.state_dict(), 'models/bone_fracture_resnet.pth')
    print("Training Complete! Model saved to models/bone_fracture_resnet.pth")

if __name__ == "__main__":
    train_model()