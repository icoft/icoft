"""RMBG-1.4 based background removal using ONNX Runtime."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _morphological_erode(mask: np.ndarray, size: int = 10) -> np.ndarray:
    """Apply morphological erosion using numpy.

    Erosion shrinks the mask, removing small artifacts at edges.
    This helps get cleaner foreground boundaries.
    """
    result = mask.copy()

    for _ in range(size):
        # Erosion: shrink True regions
        # Each pixel becomes True only if all neighbors are True
        eroded = result.copy()
        eroded[1:, :] &= result[:-1, :]  # down
        eroded[:-1, :] &= result[1:, :]  # up
        eroded[:, 1:] &= result[:, :-1]  # right
        eroded[:, :-1] &= result[:, 1:]  # left
        result = eroded

    return result


class RMBGProcessor:
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

    def __init__(self, model_path: Path | None = None):
        """Initialize RMBG-1.4 processor.

        Args:
            model_path: Path to ONNX model file. If None, uses default location.
        """
        try:
            import onnxruntime as ort  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "AI background removal requires 'onnxruntime' package. "
                "Install with: pip install icoft[ai]"
            ) from None

        self.model_path = model_path or self._get_default_model_path()

        if not self.model_path.exists():
            self._download_model()

        self.session = ort.InferenceSession(str(self.model_path))
        self.input_name = self.session.get_inputs()[0].name

    def _get_default_model_path(self) -> Path:
        """Get default model storage path."""
        cache_dir = Path.home() / ".icoft" / "models"
        return cache_dir / "rmbg-1.4.onnx"

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
    ) -> Image.Image:
        """Remove background from image using RMBG-1.4.

        Args:
            image: Input PIL Image (RGB or RGBA)

        Returns:
            PIL Image with transparent background (RGBA)
        """
        # Preprocess
        input_tensor = self._preprocess(image)

        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        mask = outputs[0][0, 0]  # Get first batch, first channel

        # Postprocess
        result_image = self._postprocess(image, mask)

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
    ) -> Image.Image:
        """Postprocess mask and apply to original image.

        Following rembg's approach:
        1. Improved normalization for RMBG-1.4 raw outputs
        2. Lower threshold for better coverage
        3. Morphological operations to fill holes and smooth edges

        Args:
            original: Original PIL Image
            mask: Predicted mask (H, W) with raw model outputs

        Returns:
            PIL Image with transparent background
        """
        # Resize mask to original image size first
        mask_raw = Image.fromarray(mask.astype(np.float32))
        mask_resized = mask_raw.resize(original.size, Image.Resampling.BILINEAR)
        mask_array = np.array(mask_resized)

        # RMBG-1.4 outputs are already probabilities in [0, 1] range
        # No need to apply sigmoid - use directly as mask probabilities
        mask_prob = mask_array

        # Use a lower threshold to better remove background
        # RMBG-1.4 is quite aggressive, so we can afford a lower threshold
        threshold = 0.35
        mask_binary = (mask_prob > threshold).astype(np.uint8)

        # Apply morphological closing to fill small holes inside the foreground
        # Then apply smoothing for better edges
        kernel_size = 5
        mask_binary = self._morphological_close(mask_binary > 0, kernel_size)

        # Convert to PIL for smoothing
        mask_pil_temp = Image.fromarray((mask_binary * 255).astype(np.uint8))

        # Apply Gaussian blur using PIL for smoother edges
        mask_pil_temp = mask_pil_temp.filter(ImageFilter.GaussianBlur(radius=3))
        mask_array_blurred = np.array(mask_pil_temp)

        # Re-threshold to get clean binary mask with smooth edges
        mask_final = (mask_array_blurred > 127).astype(np.uint8)

        mask_uint8 = mask_final.astype(np.uint8) * 255

        mask_pil = Image.fromarray(mask_uint8)

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
