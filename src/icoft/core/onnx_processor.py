"""Abstract base class for ONNX-based AI processors."""

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from PIL import Image


class ONNXProcessor(ABC):
    """Abstract base class for ONNX-based AI model processors.

    Handles common functionality like model downloading and initialization.
    Subclasses implement model-specific preprocessing and postprocessing.
    """

    MODEL_URL: str
    MODEL_SIZE_MB: float

    def __init__(self, model_path: Path | None = None) -> None:
        """Initialize ONNX processor.

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

    @abstractmethod
    def _get_default_model_path(self) -> Path:
        """Get default model storage path for this processor."""
        ...

    def _download_model(self) -> None:
        """Download model from URL."""
        import urllib.request

        print(f"Downloading model ({self.MODEL_SIZE_MB}MB)...")
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

    @abstractmethod
    def remove_background(self, image: Image.Image, **kwargs) -> Image.Image:
        """Remove background from image.

        Args:
            image: Input PIL Image
            **kwargs: Model-specific parameters

        Returns:
            PIL Image with transparent background
        """
        ...

    @abstractmethod
    def _preprocess(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for model inference.

        Args:
            image: Input PIL Image

        Returns:
            Preprocessed numpy array (1, C, H, W)
        """
        ...

    def _resize_and_normalize(
        self,
        image: Image.Image,
        input_size: int,
        mean: np.ndarray | float,
        std: np.ndarray | float,
    ) -> np.ndarray:
        """Helper method for common preprocessing steps.

        Args:
            image: Input PIL Image (will be converted to RGB)
            input_size: Target size (will be resized to input_size x input_size)
            mean: Normalization mean (scalar or array)
            std: Normalization std (scalar or array)

        Returns:
            Preprocessed numpy array (1, C, H, W)
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize to model input size
        resized = image.resize((input_size, input_size), Image.Resampling.LANCZOS)

        # Convert to numpy and normalize to [0, 1]
        img_array = np.array(resized).astype(np.float32) / 255.0

        # Normalize with mean and std
        img_array = (img_array - mean) / std

        # Transpose to (C, H, W) and add batch dimension
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)

        return img_array
