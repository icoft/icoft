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

    def extract_background_color(self) -> np.ndarray | None:
        """
        Extract background color from image edges (before AI processing).

        Randomly samples points around the edges to get a robust background color.
        Filters out outliers to avoid watermarks or noise interference.

        Returns:
            Background color as RGB array, or None if no background detected.
        """
        import random

        img_array = np.array(self.image)

        if img_array.shape[2] != 4:
            return None

        height, width = img_array.shape[:2]
        num_samples = 30  # Number of random samples per edge
        color_threshold = 20  # Threshold for considering colors similar (increased for robustness)

        # Collect opaque pixels from all four edges using random sampling
        edge_pixels = []

        # Top edge
        for _ in range(num_samples):
            x = random.randint(0, width - 1)
            pixel = img_array[0, x]
            if pixel[3] > 200:  # Only consider opaque pixels
                edge_pixels.append(pixel[:3])

        # Bottom edge
        for _ in range(num_samples):
            x = random.randint(0, width - 1)
            pixel = img_array[-1, x]
            if pixel[3] > 200:
                edge_pixels.append(pixel[:3])

        # Left edge
        for _ in range(num_samples):
            y = random.randint(0, height - 1)
            pixel = img_array[y, 0]
            if pixel[3] > 200:
                edge_pixels.append(pixel[:3])

        # Right edge
        for _ in range(num_samples):
            y = random.randint(0, height - 1)
            pixel = img_array[y, -1]
            if pixel[3] > 200:
                edge_pixels.append(pixel[:3])

        # Check if we have enough opaque pixels
        if len(edge_pixels) < 10:  # Need at least 10 opaque pixels
            return None

        # Convert to numpy array for easier processing
        pixels_array = np.array(edge_pixels)

        # Find the dominant color cluster
        # Use the first pixel as reference and find similar pixels
        reference_color = pixels_array[0]
        similar_mask = np.all(
            np.abs(pixels_array.astype(float) - reference_color.astype(float)) < color_threshold,
            axis=1,
        )
        similar_pixels = pixels_array[similar_mask]

        # If the majority are similar, use them; otherwise try different reference
        if len(similar_pixels) >= len(pixels_array) * 0.5:  # At least 50% are similar
            bg_color = np.mean(similar_pixels, axis=0)
            return bg_color

        # Try with median pixel as reference (more robust)
        median_color = np.median(pixels_array, axis=0)
        similar_mask = np.all(
            np.abs(pixels_array.astype(float) - median_color.astype(float)) < color_threshold,
            axis=1,
        )
        similar_pixels = pixels_array[similar_mask]

        if len(similar_pixels) >= len(pixels_array) * 0.5:
            bg_color = np.mean(similar_pixels, axis=0)
            return bg_color

        # If still no clear majority, return None (background too complex)
        return None

    def refine_transparency(self, bg_color: np.ndarray, tolerance: int = 10) -> "ImageProcessor":
        """
        Refine transparency using pre-extracted background color (after AI processing).

        This applies color-based transparency to remove semi-transparent artifacts
        left by AI background removal. Handles both opaque and semi-transparent pixels.

        Args:
            bg_color: Pre-extracted background color (RGB).
            tolerance: Color tolerance for background detection (0-255).

        Returns:
            self for method chaining.
        """
        img_array = np.array(self.image)

        if img_array.shape[2] != 4:
            return self

        # Find all pixels matching background color (both opaque and semi-transparent)
        color_diff = np.abs(img_array[:, :, :3].astype(float) - bg_color.astype(float))
        is_background = np.all(color_diff < tolerance, axis=2)

        # For semi-transparent regions (alpha <= 128), be more aggressive
        # They're likely AI artifacts and should be removed if they match background
        alpha = img_array[:, :, 3]
        semi_transparent_mask = alpha <= 128
        # For semi-transparent pixels, remove ALL pixels that match background color
        remove_semi_transparent = semi_transparent_mask & is_background

        # For opaque regions, also remove if matches background
        opaque_mask = alpha > 128
        remove_opaque = opaque_mask & is_background

        # Combine all removal masks
        remove_mask = remove_semi_transparent | remove_opaque

        # Set matched pixels to transparent
        alpha[remove_mask] = 0
        img_array[:, :, 3] = alpha

        self.image = Image.fromarray(img_array)
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

    def remove_background_ai(
        self,
        erode_size: int = 10,
        post_process_mask: bool = True,
        bg_threshold: int = 0,
    ) -> "ImageProcessor":
        """
        Remove background using AI (U²-Net via ONNX Runtime).

        This method uses a lightweight deep learning model to intelligently
        separate foreground from background, handling complex backgrounds
        that simple color-based methods cannot handle.

        Args:
            erode_size: Erosion size to remove edge shadows (0-50, default: 10)
                       Larger values remove more edge artifacts but may lose detail
            post_process_mask: Enable Gaussian blur for smoother edges (default: True)
            bg_threshold: Background color threshold for uncertain regions (0-255)

        Returns:
            self for method chaining.

        Raises:
            ImportError: If onnxruntime is not installed.
        """
        from .u2net import U2NetProcessor

        processor = U2NetProcessor()
        self.image = processor.remove_background(
            self.image,
            erode_size=erode_size,
            post_process_mask=post_process_mask,
            bg_threshold=bg_threshold,
        )
        return self
