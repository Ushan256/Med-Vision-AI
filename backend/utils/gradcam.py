"""
Grad-CAM (Gradient-weighted Class Activation Mapping) implementation
for Explainable AI in Medical Imaging.
"""

import torch
import torch.nn.functional as F
import cv2
import numpy as np
from typing import Tuple, Optional
import matplotlib.pyplot as plt
from PIL import Image
import torchvision.transforms as transforms


class GradCAM:
    """
    Grad-CAM implementation for generating heatmaps that highlight
    important regions in medical images for model predictions.
    """
    
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM.
        
        Args:
            model: PyTorch model
            target_layer: Target layer to compute gradients (e.g., model.layer4)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Save activation during forward pass."""
        self.activations = output
    
    def save_gradient(self, module, grad_input, grad_output):
        """Save gradient during backward pass."""
        self.gradients = grad_output[0]
    
    def generate_cam(self, input_image, class_idx=None):
        """
        Generate Class Activation Map.
        
        Args:
            input_image: Input image tensor (1, C, H, W)
            class_idx: Class index for which to generate CAM (None for predicted class)
            
        Returns:
            cam: Class activation map as numpy array
        """
        self.model.eval()
        
        # Forward pass
        output = self.model(input_image)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1)
        
        # Backward pass
        self.model.zero_grad()
        class_loss = output[0, class_idx]
        class_loss.backward()
        
        # Get gradients and activations
        gradients = self.gradients[0]  # Shape: (C, H, W)
        activations = self.activations[0]  # Shape: (C, H, W)
        
        # Compute weights (global average pooling of gradients)
        weights = torch.mean(gradients, dim=(1, 2))  # Shape: (C,)
        
        # Generate CAM
        cam = torch.zeros(activations.shape[1:], dtype=torch.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i, :, :]
        
        # Apply ReLU
        cam = F.relu(cam)
        
        # Normalize
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        return cam.cpu().numpy()
    
    def overlay_heatmap(self, image, cam, alpha=0.4, colormap=cv2.COLORMAP_JET):
        """
        Overlay heatmap on original image.
        
        Args:
            image: Original image (numpy array, H, W, 3) in range [0, 255]
            cam: Class activation map (numpy array, H, W)
            alpha: Transparency factor for overlay
            colormap: OpenCV colormap
            
        Returns:
            overlayed_image: Image with heatmap overlay
        """
        # Resize CAM to match image size
        cam_resized = cv2.resize(cam, (image.shape[1], image.shape[0]))
        cam_resized = np.uint8(255 * cam_resized)
        
        # Apply colormap
        heatmap = cv2.applyColorMap(cam_resized, colormap)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Overlay
        overlayed = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
        
        return overlayed


def generate_gradcam_heatmap(
    model,
    image_path: str,
    target_layer,
    class_idx: Optional[int] = None,
    image_size: int = 224
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Generate Grad-CAM heatmap for a given image.
    
    Args:
        model: PyTorch model
        image_path: Path to input image
        target_layer: Target layer for Grad-CAM (e.g., model.layer4)
        class_idx: Class index for CAM (None for predicted class)
        image_size: Target image size
        
    Returns:
        original_image: Original image as numpy array
        heatmap_overlay: Image with heatmap overlay
        predicted_class: Predicted class index
    """
    # Load and preprocess image
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    original_image = np.array(image)
    image_tensor = transform(image).unsqueeze(0)
    
    # Get prediction
    model.eval()
    with torch.no_grad():
        output = model(image_tensor)
        predicted_class = output.argmax(dim=1).item()
        probabilities = F.softmax(output, dim=1)[0]
    
    # Generate Grad-CAM
    gradcam = GradCAM(model, target_layer)
    cam = gradcam.generate_cam(image_tensor, class_idx=class_idx if class_idx is not None else predicted_class)
    
    # Overlay heatmap
    heatmap_overlay = gradcam.overlay_heatmap(original_image, cam)
    
    return original_image, heatmap_overlay, predicted_class, probabilities


def visualize_gradcam(
    original_image: np.ndarray,
    heatmap_overlay: np.ndarray,
    predicted_class: int,
    class_names: list,
    probabilities: torch.Tensor,
    save_path: Optional[str] = None
):
    """
    Visualize Grad-CAM results.
    
    Args:
        original_image: Original image
        heatmap_overlay: Image with heatmap overlay
        predicted_class: Predicted class index
        class_names: List of class names
        probabilities: Class probabilities
        save_path: Optional path to save the visualization
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Original image
    axes[0].imshow(original_image)
    axes[0].set_title("Original Image", fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    # Heatmap overlay
    axes[1].imshow(heatmap_overlay)
    title = f"Grad-CAM Heatmap\nPredicted: {class_names[predicted_class]} ({probabilities[predicted_class]*100:.2f}%)"
    axes[1].set_title(title, fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    
    plt.show()
