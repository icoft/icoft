"""RMBG-1.4 based background removal using ONNX Runtime.

RMBG-1.4 is a specialized background removal model that generally produces
better results than U²-Net, especially for complex edges and hollow shapes.

Key differences from U²-Net:
- Better handling of hollow shapes (donuts, rings, letters with holes)
- Smoother edge transitions (but may require threshold tuning)
- Larger model size (~45MB quantized vs ~5MB for U²-Net)
- Slower inference (~1s vs ~0.5s for U²-Net)

Recommended threshold values:
- 100-128: For light foreground on gray background (e.g., white icons)
- 180-220: For dark foreground on light background (e.g., dark logos)
"""

from pathlib import Path

import numpy as np
from PIL import Image


class RMBGProcessor:
    """RMBG-1.4 processor for AI-based background removal.

    Uses ONNX Runtime for inference with the quantized RMBG-1.4 model.
    Model is automatically downloaded on first use.

    Args:
        model_path: Path to ONNX model file. If None, uses default location.
        threshold: Threshold for binarizing mask (0-255). Default 200.
                   Lower values = more aggressive background removal.
                   Higher values = preserve more foreground details.
    """

    MODEL_URL = "https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model_quantized.onnx"
    MODEL_SIZE_MB = 45

    def __init__(self, model_path: Path | None = None, threshold: int = 200):
        """Initialize RMBG-1.4 processor.

        Args:
            model_path: Path to ONNX model file. If None, uses default location.
            threshold: Threshold for binarizing mask (0-255). Default 200.
        """
        try:
            import onnxruntime as ort  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "AI background removal requires 'onnxruntime' package. "
                "Install with: pip install icoft[ai]"
            ) from None

        self.model_path = model_path or self._get_default_model_path()
        self.threshold = threshold

        if not self.model_path.exists():
            self._download_model()

        # Use CPU execution provider for compatibility
        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def _get_default_model_path(self) -> Path:
        """Get default model storage path."""
        cache_dir = Path.home() / ".rmbg"
        return cache_dir / "model_quantized.onnx"

    def _download_model(self) -> None:
        """Download RMBG-1.4 model from HuggingFace."""
        import urllib.request

        print(f"Downloading RMBG-1.4 model ({self.MODEL_SIZE_MB}MB)...")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        def reporthook(block_num: int, block_size: int, total_size: int) -> None:
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

        urllib.request.urlretrieve(self.MODEL_URL, str(self.model_path), reporthook)
        print(f"\nModel downloaded to {self.model_path}")

    def remove_background(
        self,
        image: Image.Image,
        threshold: int | None = None,
    ) -> Image.Image:
        """Remove background from image using RMBG-1.4.

        Args:
            image: Input PIL Image (RGB or RGBA)
            threshold: Optional override for threshold (0-255).
                      If None, uses the instance default.

        Returns:
            PIL Image with transparent background (RGBA)
        """
        # Use provided threshold or instance default
        thresh = threshold if threshold is not None else self.threshold

        # Store original size
        original_size = image.size

        # Preprocess
        input_tensor = self._preprocess(image)

        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        mask = outputs[0][0, 0]  # Get first batch, first channel

        # Postprocess
        result_image = self._postprocess(
            image,
            mask,
            original_size=original_size,
            threshold=thresh,
        )

        return result_image

    def _preprocess(self, image: Image.Image, input_size: int = 1024) -> np.ndarray:
        """Preprocess image for RMBG-1.4 inference.

        Args:
            image: Input PIL Image
            input_size: Model input size (default 1024x1024)

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

        # RMBG-1.4 uses different normalization: normalize to [-0.5, 0.5]
        # mean = [0.5, 0.5, 0.5], std = [1.0, 1.0, 1.0]
        mean = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        std = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        img_array = (img_array - mean) / std

        # Transpose to (C, H, W) and add batch dimension
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def _postprocess(
        self,
        original: Image.Image,
        mask: np.ndarray,
        original_size: tuple[int, int],
        threshold: int = 200,
    ) -> Image.Image:
        """Postprocess mask and apply to original image.

        Args:
            original: Original PIL Image
            mask: Predicted mask (H, W) with raw model output values
            original_size: Original image size (width, height)
            threshold: Threshold for binarizing mask (0-255)

        Returns:
            PIL Image with transparent background
        """
        # Normalize mask to [0, 1] range (min-max normalization)
        mask_min = mask.min()
        mask_max = mask.max()
        mask_normalized = (
            (mask - mask_min) / (mask_max - mask_min) if mask_max > mask_min else mask
        )

        # Convert to uint8
        mask_uint8 = (mask_normalized * 255).astype(np.uint8)

        # Apply threshold to clean up background
        # Values below threshold become 0 (transparent)
        # Values above threshold become 255 (opaque)
        mask_binary = np.where(mask_uint8 < threshold, 0, 255).astype(np.uint8)

        # Resize mask to original image size
        mask_pil = Image.fromarray(mask_binary)
        mask_resized = mask_pil.resize(original_size, Image.Resampling.BILINEAR)

        # Ensure original is RGBA
        if original.mode != "RGBA":
            original = original.convert("RGBA")

        # Apply mask as alpha channel
        r, g, b, _ = original.split()
        result = Image.merge("RGBA", (r, g, b, mask_resized))

        return result
