import base64
import io
from typing import Optional

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image


def find_last_conv_layer(model: nn.Module) -> nn.Module:
    for name, module in reversed(list(model.named_modules())):
        if isinstance(module, nn.Conv2d):
            return module
    raise ValueError("No Conv2d layer found in model")


class GradCAMService:
    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        self.model = model
        self.target_layer = (
            target_layer if target_layer else find_last_conv_layer(model)
        )

    def generate(
        self,
        image_bytes: bytes,
        input_tensor: torch.Tensor,
        class_idx: int,
    ) -> str:
        self.model.eval()
        gradients = []
        activations = []

        def backward_hook(module, grad_input, grad_output):
            gradients.append(grad_output[0])

        def forward_hook(module, input, output):
            activations.append(output)

        handle_forward = self.target_layer.register_forward_hook(forward_hook)
        handle_backward = self.target_layer.register_full_backward_hook(backward_hook)

        output = self.model(input_tensor)
        self.model.zero_grad()

        one_hot = torch.zeros_like(output)
        one_hot[0, class_idx] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        handle_forward.remove()
        handle_backward.remove()

        if not activations or not gradients:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_np = np.array(img.resize((224, 224)))
            _, buffer = cv2.imencode(".png", cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
            return base64.b64encode(buffer).decode("utf-8")

        gradient = gradients[0].cpu().data.numpy()[0]
        activation = activations[0].cpu().data.numpy()[0]

        weights = np.mean(gradient, axis=(1, 2))
        cam = np.zeros(activation.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            cam += w * activation[i]

        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam = cam / cam.max()

        cam = cv2.resize(cam, (224, 224))

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(img.resize((224, 224))) / 255.0

        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = np.float32(heatmap) / 255
        heatmap = heatmap[..., ::-1]

        cam_image = heatmap * 0.4 + np.float32(img_np) * 0.6
        cam_image = np.clip(cam_image, 0, 1)

        _, buffer = cv2.imencode(".png", np.uint8(255 * cam_image))
        return base64.b64encode(buffer).decode("utf-8")
