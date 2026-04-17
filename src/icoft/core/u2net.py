"""U²-Net based background removal using ONNX Runtime."""

from pathlib import Path

import numpy as np
from PIL import Image

from .onnx_processor import ONNXProcessor


class U2NetProcessor(ONNXProcessor):
    """U²-Net processor for AI-based background removal.

    Uses ONNX Runtime for inference with the lightweight u2netp model.
    Model is automatically downloaded on first use.
    """

    MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx"
    MODEL_SIZE_MB = 4.7

    def _get_default_model_path(self) -> Path:
        """Get default model storage path."""
        cache_dir = Path.home() / ".u2net"
        return cache_dir / "u2netp.onnx"

    def remove_background(
        self,
        image: Image.Image,
        erode_size: int = 0,
        post_process_mask: bool = True,
        bg_threshold: int = 0,
        **kwargs,  # noqa: ARG002 - Accept extra kwargs for interface compatibility
    ) -> Image.Image:
        """Remove background from image using U²-Net.

        Args:
            image: Input PIL Image (RGB or RGBA)
            erode_size: Erosion size to remove edge shadows (0-50, larger=more erosion)
            post_process_mask: Enable mask post-processing for smoother edges

        Returns:
            PIL Image with transparent background (RGBA)
        """
        # Preprocess
        input_tensor = self._preprocess(image)

        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        mask = outputs[0][
            0, 0
        ]  # Get first batch, first channel (already in [0,1] range via sigmoid)

        # Postprocess
        result_image = self._postprocess(
            image,
            mask,
            erode_size=erode_size,
            post_process_mask=post_process_mask,
            bg_threshold=bg_threshold,
        )

        return result_image

    def _preprocess(self, image: Image.Image, input_size: int = 320) -> np.ndarray:
        """Preprocess image for U²-Net inference.

        Args:
            image: Input PIL Image
            input_size: Model input size (default 320x320)

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

        # Normalize with ImageNet stats
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_array = (img_array - mean) / std

        # Transpose to (C, H, W) and add batch dimension
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def _postprocess(
        self,
        original: Image.Image,
        mask: np.ndarray,
        erode_size: int = 0,  # noqa: ARG002
        post_process_mask: bool = True,  # noqa: ARG002
        bg_threshold: int = 0,  # noqa: ARG002
    ) -> Image.Image:
        """Postprocess mask and apply to original image.

        Args:
            original: Original PIL Image
            mask: Predicted mask (H, W) with values in [0, 1]
            erode_size: Erosion size to remove edge shadows
            post_process_mask: Enable mask post-processing
            bg_threshold: Color threshold for uncertain edge regions

        Returns:
            PIL Image with transparent background
        """
        # Resize mask to original image size first
        mask_uint8 = (mask * 255).astype(np.uint8)
        mask_pil = Image.fromarray(mask_uint8)
        mask_resized = mask_pil.resize(original.size, Image.Resampling.BILINEAR)
        mask_array = np.array(mask_resized)

        # Smart edge refinement: use original image colors to clean up AI artifacts

        mask_pil_clean = Image.fromarray(mask_array.astype(np.uint8))

        # TODO: Post-processing causes object shrinkage - disabled for now
        # Apply erosion using PIL morphology if erode_size > 0
        # if erode_size > 0:
        #     from PIL import ImageFilter
        #     kernel_size = max(3, erode_size)
        #     if kernel_size % 2 == 0:
        #         kernel_size += 1
        #     mask_pil_clean = mask_pil_clean.filter(ImageFilter.MinFilter(kernel_size))

        # TODO: Gaussian blur disabled - causes edge softening
        # if post_process_mask:
        #     from PIL import ImageFilter
        #     mask_pil_clean = mask_pil_clean.filter(ImageFilter.GaussianBlur(radius=1))

        # Ensure original is RGBA
        if original.mode != "RGBA":
            original = original.convert("RGBA")

        # Apply mask as alpha channel
        r, g, b, a = original.split()
        a = mask_pil_clean
        result = Image.merge("RGBA", (r, g, b, a))

        return result
