"""RMBG-1.4 based background removal using ONNX Runtime."""

from pathlib import Path

import numpy as np
from PIL import Image

from .onnx_processor import ONNXProcessor


class RMBGProcessor(ONNXProcessor):
    """RMBG-1.4 processor for AI-based background removal.

    Uses ONNX Runtime for inference with the RMBG-1.4 model.
    Model is automatically downloaded on first use.
    """

    # Model variants available:
    # - model.onnx: 176MB (full precision)
    # - model_fp16.onnx: 88MB (half precision)
    # - model_quantized.onnx: 44MB (INT8 quantized, recommended)
    MODEL_URL = "https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model_quantized.onnx"
    MODEL_SIZE_MB = 44  # Quantized version

    def _get_default_model_path(self) -> Path:
        """Get default model storage path."""
        cache_dir = Path.home() / ".icoft" / "models"
        return cache_dir / "rmbg-1.4.onnx"

    def remove_background(
        self,
        image: Image.Image,
        threshold: float = 0.997,
        kernel_size: int = 10,
        **kwargs,  # noqa: ARG002 - Accept extra kwargs for interface compatibility
    ) -> Image.Image:
        """Remove background from image using RMBG-1.4.

        Args:
            image: Input PIL Image (RGB or RGBA)
            threshold: Binarization threshold (0-1, default: 0.997, higher = more aggressive)
            kernel_size: Morphological closing kernel size (default: 10, larger = better hole filling)

        Returns:
            PIL Image with transparent background (RGBA)
        """
        # Preprocess
        input_tensor = self._preprocess(image)

        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        mask = outputs[0][0, 0]  # Get first batch, first channel

        # Postprocess
        result_image = self._postprocess(image, mask, threshold=threshold, kernel_size=kernel_size)

        return result_image

    def _preprocess(self, image: Image.Image, input_size: int = 1024) -> np.ndarray:
        """Preprocess image for RMBG-1.4 inference.

        Official RMBG-1.4 preprocessing:
        1. Resize to 1024x1024
        2. Normalize to [0, 1]
        3. Normalize with mean=[0.5, 0.5, 0.5], std=[1.0, 1.0, 1.0]
           (i.e., x = (x - 0.5) / 1.0 = x - 0.5, range [-0.5, 0.5])

        Args:
            image: Input PIL Image
            input_size: Model input size (default 1024x1024 for RMBG-1.4)

        Returns:
            Preprocessed numpy array (1, 3, H, W)
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize to model input size
        resized = image.resize((input_size, input_size), Image.Resampling.LANCZOS)

        # Convert to numpy and normalize to [0, 1]
        img_array = np.array(resized).astype(np.float32) / 255.0

        # RMBG-1.4 official normalization: mean=0.5, std=1.0
        # Result range: [-0.5, 0.5]
        img_array = img_array - 0.5

        # Transpose to (C, H, W) and add batch dimension
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def _postprocess(
        self,
        original: Image.Image,
        mask: np.ndarray,
        threshold: float = 0.997,
        kernel_size: int = 10,
    ) -> Image.Image:
        """Postprocess mask and apply to original image.

        Following rembg's approach:
        1. Improved normalization for RMBG-1.4 raw outputs
        2. Lower threshold for better coverage
        3. Morphological operations to fill holes and smooth edges

        Args:
            original: Original PIL Image
            mask: Predicted mask (H, W) with raw model outputs
            threshold: Binarization threshold (0-1, default: 0.997)
            kernel_size: Morphological closing kernel size (default: 10)

        Returns:
            PIL Image with transparent background
        """
        # Resize mask to original image size first
        mask_raw = Image.fromarray(mask.astype(np.float32))
        mask_resized = mask_raw.resize(original.size, Image.Resampling.BILINEAR)
        mask_array = np.array(mask_resized)

        # Use a moderate threshold to balance foreground/background separation
        # RMBG-1.4 outputs are already probabilities in [0, 1] range
        mask_prob = mask_array

        # If threshold >= 1.0, skip binarization and use continuous alpha
        if threshold >= 1.0:
            mask_final = (mask_prob * 255).astype(np.uint8)
        else:
            mask_binary = (mask_prob >= threshold).astype(np.uint8)

            # Apply morphological closing to fill small holes inside the foreground
            mask_binary = self._morphological_close(mask_binary > 0, kernel_size)
            mask_final = (mask_binary * 255).astype(np.uint8)

        mask_pil = Image.fromarray(mask_final)

        # Ensure original is RGBA
        if original.mode != "RGBA":
            original = original.convert("RGBA")

        # Apply mask as alpha channel
        r, g, b, _ = original.split()
        result = Image.merge("RGBA", (r, g, b, mask_pil))

        return result

    def _morphological_close(self, mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Apply morphological closing to fill small holes.

        Closing = dilation followed by erosion
        This fills small holes inside the foreground while maintaining the overall shape.
        """
        # Dilation: expand True regions
        dilated = mask.copy()
        for _ in range(kernel_size):
            expanded = dilated.copy()
            expanded[1:, :] |= dilated[:-1, :]  # down
            expanded[:-1, :] |= dilated[1:, :]  # up
            expanded[:, 1:] |= dilated[:, :-1]  # right
            expanded[:, :-1] |= dilated[:, 1:]  # left
            dilated = expanded

        # Erosion: shrink back to original size
        eroded = dilated.copy()
        for _ in range(kernel_size):
            contracted = eroded.copy()
            contracted[1:, :] &= dilated[:-1, :]
            contracted[:-1, :] &= dilated[1:, :]
            contracted[:, 1:] &= dilated[:, :-1]
            contracted[:, :-1] &= dilated[:, 1:]
            eroded = contracted

        return eroded

    def _morphological_open(self, mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Apply morphological opening to remove isolated noise pixels.

        Opening = erosion followed by dilation
        This removes small isolated pixels while preserving larger structures.
        """
        # Erosion: shrink True regions (removes isolated pixels)
        eroded = mask.copy()
        for _ in range(kernel_size):
            contracted = eroded.copy()
            contracted[1:, :] &= eroded[:-1, :]
            contracted[:-1, :] &= eroded[1:, :]
            contracted[:, 1:] &= eroded[:, :-1]
            contracted[:, :-1] &= eroded[:, 1:]
            eroded = contracted

        # Dilation: expand back to restore original size
        dilated = eroded.copy()
        for _ in range(kernel_size):
            expanded = dilated.copy()
            expanded[1:, :] |= eroded[:-1, :]
            expanded[:-1, :] |= eroded[1:, :]
            expanded[:, 1:] |= eroded[:, :-1]
            expanded[:, :-1] |= eroded[:, 1:]
            dilated = expanded

        return dilated
