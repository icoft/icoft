"""Image preprocessing module for Icoft."""

from pathlib import Path

import numpy as np
from PIL import Image


class ImageProcessor:
    """
    Image processor for AI-generated logos.

    Handles cropping, background removal, and noise reduction.
    """

    def __init__(self, image_path: str | Path) -> None:
        """
        Initialize the image processor.

        Args:
            image_path: Path to the input image file.
        """
        self.image_path = Path(image_path)
        self.image = Image.open(self.image_path).convert("RGBA")
        self.original_image = self.image.copy()

    def crop_borders(self, margin: str = "5%") -> "ImageProcessor":
        """
        Crop borders from the image by the specified margin.

        This simply crops the edges by the margin amount to remove
        watermarks or quality issues at the borders.

        Args:
            margin: Margin percentage to crop from edges (e.g., "10%" or "5px").

        Returns:
            self for method chaining.
        """
        margin_value = self._parse_margin(margin, self.image.size)

        if margin_value > 0:
            width, height = self.image.size

            # Calculate crop box (crop from all edges by margin_value)
            left = margin_value
            upper = margin_value
            right = width - margin_value
            lower = height - margin_value

            # Ensure valid crop box
            if left < right and upper < lower:
                self.image = self.image.crop((left, upper, right, lower))

        return self

    def make_background_transparent(self, tolerance: int = 10) -> "ImageProcessor":
        """
        Convert single-color background to transparent.

        Args:
            tolerance: Color tolerance for background detection (0-255).

        Returns:
            self for method chaining.
        """
        img_array = np.array(self.image)

        if img_array.shape[2] == 4:
            corners = [
                img_array[0, 0],
                img_array[0, -1],
                img_array[-1, 0],
                img_array[-1, -1],
            ]

            bg_colors = []
            for corner in corners:
                if corner[3] > 200:
                    bg_colors.append(corner[:3])

            if bg_colors:
                bg_color = np.mean(bg_colors, axis=0)
                alpha = img_array[:, :, 3]
                is_background = np.all(
                    np.abs(img_array[:, :, :3].astype(float) - bg_color) < tolerance, axis=2
                )
                alpha[is_background] = 0
                img_array[:, :, 3] = alpha

        self.image = Image.fromarray(img_array)
        return self

    def resize(self, size: tuple[int, int], sharpen: bool = True) -> "ImageProcessor":
        """
        Resize the image to the specified size with optional sharpening.

        Args:
            size: Target size as (width, height).
            sharpen: Apply sharpening for small sizes (< 64px).

        Returns:
            self for method chaining.
        """
        from PIL import ImageFilter

        target_size = min(size)

        self.image = self.image.resize(size, Image.Resampling.LANCZOS)

        if sharpen and target_size < 64:
            if target_size < 32:
                sharpness = 180
            elif target_size < 48:
                sharpness = 150
            else:
                sharpness = 130

            self.image = self.image.filter(
                ImageFilter.UnsharpMask(radius=1, percent=sharpness, threshold=3)
            )

        return self

    def save(self, output_path: str | Path) -> None:
        """
        Save the processed image.

        Args:
            output_path: Path to save the image.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(output_path, "PNG")

    def _parse_margin(self, margin: str, image_size: tuple[int, int]) -> int:
        """
        Parse margin string to pixel value.

        Args:
            margin: Margin string (e.g., "10%" or "5px").
            image_size: Image size as (width, height).

        Returns:
            Margin value in pixels.
        """
        margin = margin.strip()

        if margin.endswith("%"):
            percentage = float(margin[:-1]) / 100.0
            return int(min(image_size) * percentage)
        elif margin.endswith("px"):
            return int(margin[:-2])
        else:
            try:
                return int(float(margin))
            except ValueError:
                return int(min(image_size) * 0.1)

    def _add_margin(self, margin_pixels: int) -> None:
        """
        Add margin around the image.

        Args:
            margin_pixels: Margin size in pixels.
        """
        if margin_pixels <= 0:
            return

        width, height = self.image.size
        new_width = width + 2 * margin_pixels
        new_height = height + 2 * margin_pixels

        new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        new_image.paste(self.image, (margin_pixels, margin_pixels))
        self.image = new_image

    def remove_background_ai(self) -> "ImageProcessor":
        """
        Remove background using AI (U²-Net via ONNX Runtime).

        This method uses a lightweight deep learning model to intelligently
        separate foreground from background, handling complex backgrounds
        that simple color-based methods cannot handle.

        Returns:
            self for method chaining.

        Raises:
            ImportError: If onnxruntime is not installed.
        """
        from .u2net import U2NetProcessor

        processor = U2NetProcessor()
        self.image = processor.remove_background(self.image)
        return self
