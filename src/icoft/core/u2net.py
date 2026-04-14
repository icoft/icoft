"""U²-Net based background removal using ONNX Runtime."""

from pathlib import Path

import numpy as np
from PIL import Image


class U2NetProcessor:
    """U²-Net processor for AI-based background removal.

    Uses ONNX Runtime for inference with the lightweight u2netp model.
    Model is automatically downloaded on first use.
    """

    MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx"
    MODEL_SIZE_MB = 4.7

    def __init__(self, model_path: Path | None = None):
        """Initialize U²-Net processor.

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
        cache_dir = Path.home() / ".u2net"
        return cache_dir / "u2netp.onnx"

    def _download_model(self) -> None:
        """Download U²-Netp model from rembg releases."""
        import urllib.request

        print(f"Downloading U²-Netp model ({self.MODEL_SIZE_MB}MB)...")
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
        erode_size: int = 0,
        post_process_mask: bool = True,
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
        mask = outputs[0][0, 0]  # Get first batch, first channel

        # Postprocess
        result_image = self._postprocess(
            image,
            mask,
            erode_size=erode_size,
            post_process_mask=post_process_mask,
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
        erode_size: int = 0,
        post_process_mask: bool = True,
    ) -> Image.Image:
        """Postprocess mask and apply to original image.

        Args:
            original: Original PIL Image
            mask: Predicted mask (H, W) with values in [0, 1]
            erode_size: Erosion size to remove edge shadows
            post_process_mask: Enable mask post-processing

        Returns:
            PIL Image with transparent background
        """
        # Resize mask to original image size first
        mask_uint8 = (mask * 255).astype(np.uint8)
        mask_pil = Image.fromarray(mask_uint8)
        mask_resized = mask_pil.resize(original.size, Image.Resampling.BILINEAR)
        mask_array = np.array(mask_resized)

        # Smart edge refinement: use original image colors to clean up AI artifacts
        # Get the original image as numpy array
        if original.mode != "RGBA":
            original_rgb = original.convert("RGB")
        else:
            original_rgb = original.convert("RGB")
        
        original_array = np.array(original_rgb)
        
        # Detect background color from corners (assuming corners are background)
        h, w = original_array.shape[:2]
        corner_samples = [
            original_array[0, 0],
            original_array[0, w-1],
            original_array[h-1, 0],
            original_array[h-1, w-1],
        ]
        bg_color = np.mean(corner_samples, axis=0)
        
        # For uncertain edge regions (128-200), check if they match background color
        # If yes, make them transparent even if model says they're foreground
        uncertain_mask = (mask_array > 128) & (mask_array < 200)
        if np.any(uncertain_mask):
            # Calculate color distance to background
            color_diff = np.abs(original_array.astype(float) - bg_color)
            is_bg_color = np.all(color_diff < 40, axis=2)  # Tolerance of 40
            
            # Make uncertain regions transparent if they match background color
            mask_array[uncertain_mask & is_bg_color] = 0

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
