"""
Training script for Medical AI model.
Implements Transfer Learning using ResNet18 for chest X-ray pneumonia classification.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
import kagglehub
import os
import sys
from pathlib import Path
from tqdm import tqdm


def get_data_loaders(dataset_path, batch_size=32, image_size=224):
    """
    Create data loaders for training and validation.
    
    Args:
        dataset_path: Path to the dataset directory
        batch_size: Batch size for training
        image_size: Target image size for resizing
        
    Returns:
        train_loader, val_loader: DataLoader objects for training and validation
    """
    # Data augmentation and normalization for training
    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Only normalization for validation
    val_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Find train and test directories
    dataset_path = Path(dataset_path)
    train_dir = dataset_path / "chest_xray" / "train"
    test_dir = dataset_path / "chest_xray" / "test"
    
    if not train_dir.exists():
        # Try alternative structure
        train_dir = dataset_path / "train"
        test_dir = dataset_path / "test"
    
    # Create datasets
    train_dataset = ImageFolder(root=str(train_dir), transform=train_transform)
    val_dataset = ImageFolder(root=str(test_dir), transform=val_transform)
    
    # Set num_workers based on OS (Windows has issues with multiprocessing)
    num_workers = 0 if sys.platform == 'win32' else 2
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Classes: {train_dataset.classes}")
    
    return train_loader, val_loader, train_dataset.classes


def create_model(num_classes=2):
    """
    Create a ResNet18 model with transfer learning.
    
    Args:
        num_classes: Number of output classes (default: 2 for Normal/Pneumonia)
        
    Returns:
        model: PyTorch model
    """
    # Load pre-trained ResNet18
    model = models.resnet18(weights='IMAGENET1K_V1')
    
    # Freeze all layers except the final classifier
    for param in model.parameters():
        param.requires_grad = False
    
    # Replace the final fully connected layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    # Unfreeze the final layer for training
    for param in model.fc.parameters():
        param.requires_grad = True
    
    return model


def train_epoch(model, train_loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for images, labels in tqdm(train_loader, desc="Training"):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100 * correct / total
    return epoch_loss, epoch_acc


def validate(model, val_loader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="Validating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    epoch_loss = running_loss / len(val_loader)
    epoch_acc = 100 * correct / total
    return epoch_loss, epoch_acc


def train_model(dataset_path=None, epochs=5, batch_size=32, lr=0.001):
    """
    Main training function.
    
    Args:
        dataset_path: Path to dataset (if None, downloads from Kaggle)
        epochs: Number of training epochs
        batch_size: Batch size for training
        lr: Learning rate
    """
    # Get dataset path
    if dataset_path is None:
        print("Downloading dataset from Kaggle...")
        dataset_path = kagglehub.dataset_download("paultimothymooney/chest-xray-pneumonia")
        print(f"Dataset path: {dataset_path}")
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Get data loaders
    train_loader, val_loader, classes = get_data_loaders(dataset_path, batch_size=batch_size)
    
    # Create model
    model = create_model(num_classes=len(classes))
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=lr)
    
    # Training loop
    print(f"\nStarting training for {epochs} epochs...")
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 50)
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            model_path = Path(__file__).parent / "models" / "medical_model.pth"
            model_path.parent.mkdir(exist_ok=True)
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': classes,
                'epoch': epoch,
                'val_acc': val_acc
            }, model_path)
            print(f"Saved best model with validation accuracy: {val_acc:.2f}%")
    
    print(f"\nTraining completed! Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: models/medical_model.pth")


if __name__ == "__main__":
    train_model(epochs=5, batch_size=32, lr=0.001)
