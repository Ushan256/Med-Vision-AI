"""
Professional Grad-CAM (Gradient-weighted Class Activation Mapping) implementation
for Explainable AI in Medical Imaging with ResNet18.

This module provides functionality to visualize which regions of an input image
are most important for the model's prediction.
"""

import torch
import torch.nn.functional as F
import cv2
import numpy as np
from typing import Optional, Union
from PIL import Image


class GradCAMHook:
    """
    Hook class to capture gradients and activations from a target layer.
    """
    
    def __init__(self):
        self.gradients = None
        self.activations = None
    
    def save_gradient(self, grad):
        """Save gradient during backward pass."""
        self.gradients = grad
    
    def save_activation(self, activation):
        """Save activation during forward pass."""
        self.activations = activation
    
    def get_hooks(self):
        """Return forward and backward hooks."""
        def forward_hook(module, input, output):
            self.save_activation(output)
        
        def backward_hook(module, grad_input, grad_output):
            # grad_output is a tuple, take the first element
            if grad_output[0] is not None:
                self.save_gradient(grad_output[0])
        
        return forward_hook, backward_hook


def generate_gradcam(
    model: torch.nn.Module,
    input_tensor: torch.Tensor,
    target_layer: torch.nn.Module,
    class_idx: Optional[int] = None,
    original_image: Optional[np.ndarray] = None
) -> Union[np.ndarray, Image.Image]:
    """
    Generate Grad-CAM heatmap and overlay it on the original image.
    
    This function extracts gradients from the target layer (typically the last
    convolutional layer of ResNet18) and generates a heatmap showing which
    regions of the image are most important for the model's prediction.
    
    Args:
        model: PyTorch model (should be in eval mode)
        input_tensor: Preprocessed input image tensor of shape (1, C, H, W)
        target_layer: Target convolutional layer to extract gradients from
                      (e.g., model.layer4 for ResNet18)
        class_idx: Class index for which to generate CAM. If None, uses the
                   predicted class.
        original_image: Original image as numpy array (H, W, 3) in range [0, 255].
                        If None, will be extracted from input_tensor.
    
    Returns:
        Final image with heatmap overlay as numpy array (H, W, 3) in range [0, 255],
        ready for Base64 encoding or PIL Image conversion.
    
    Example:
        >>> model.eval()
        >>> target_layer = model.layer4  # Last conv layer in ResNet18
        >>> result = generate_gradcam(model, input_tensor, target_layer)
        >>> # Convert to PIL Image if needed
        >>> pil_image = Image.fromarray(result.astype(np.uint8))
    """
    model.eval()
    
    # Initialize hook
    hook = GradCAMHook()
    forward_hook, backward_hook = hook.get_hooks()
    
    # Register hooks
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_full_backward_hook(backward_hook)
    
    try:
        # Forward pass
        output = model(input_tensor)
        
        # Determine class index
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        
        # Backward pass
        model.zero_grad()
        # Get the score for the target class
        score = output[0, class_idx]
        score.backward()
        
        # Get gradients and activations
        gradients = hook.gradients  # Shape: (B, C, H, W)
        activations = hook.activations  # Shape: (B, C, H, W)
        
        if gradients is None or activations is None:
            raise ValueError("Failed to capture gradients or activations. "
                           "Ensure the model is in eval mode and gradients are enabled.")
        
        # Remove batch dimension
        gradients = gradients[0]  # Shape: (C, H, W)
        activations = activations[0]  # Shape: (C, H, W)
        
        # Compute weights: global average pooling of gradients
        # This gives us the importance of each feature map
        weights = torch.mean(gradients, dim=(1, 2))  # Shape: (C,)
        
        # Generate Class Activation Map (CAM)
        # Weighted sum of activation maps
        cam = torch.zeros(activations.shape[1:], dtype=torch.float32, device=activations.device)
        for i, weight in enumerate(weights):
            cam += weight * activations[i, :, :]
        
        # Apply ReLU to only show positive contributions
        cam = F.relu(cam)
        
        # Normalize CAM to [0, 1]
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)
        
        # Convert to numpy
        cam = cam.detach().cpu().numpy()
        
        # Get original image dimensions
        if original_image is None:
            # Reconstruct from input_tensor (denormalize)
            img_tensor = input_tensor[0].cpu().clone()
            # Denormalize ImageNet normalization
            mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            img_tensor = img_tensor * std + mean
            img_tensor = torch.clamp(img_tensor, 0, 1)
            # Convert to numpy and scale to [0, 255]
            original_image = (img_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
        
        # Resize CAM to match original image size
        original_h, original_w = original_image.shape[:2]
        cam_resized = cv2.resize(cam, (original_w, original_h))
        cam_resized = np.clip(cam_resized, 0, 1)
        
        # Convert CAM to heatmap using colormap
        cam_uint8 = np.uint8(255 * cam_resized)
        heatmap = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Ensure original_image is in the correct format
        if original_image.dtype != np.uint8:
            original_image = (np.clip(original_image, 0, 255)).astype(np.uint8)
        
        # Overlay heatmap on original image
        # Alpha controls the transparency: 0.4 means 40% heatmap, 60% original
        alpha = 0.4
        overlayed_image = cv2.addWeighted(original_image, 1 - alpha, heatmap, alpha, 0)
        
        # Ensure output is in correct format [0, 255] uint8
        overlayed_image = np.clip(overlayed_image, 0, 255).astype(np.uint8)
        
        return overlayed_image
    
    finally:
        # Remove hooks to prevent memory leaks
        forward_handle.remove()
        backward_handle.remove()


def get_resnet18_target_layer(model: torch.nn.Module) -> torch.nn.Module:
    """
    Get the last convolutional layer of ResNet18 for Grad-CAM.
    
    Args:
        model: ResNet18 model
    
    Returns:
        The last convolutional layer (model.layer4)
    
    Example:
        >>> target_layer = get_resnet18_target_layer(model)
        >>> result = generate_gradcam(model, input_tensor, target_layer)
    """
    # For ResNet18, layer4 is the last convolutional block
    # This contains the final feature maps before global average pooling
    if hasattr(model, 'layer4'):
        return model.layer4
    else:
        raise ValueError("Model does not have 'layer4' attribute. "
                       "This function is designed for ResNet18 architecture.")
