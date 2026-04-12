"""
Advanced smart cutout algorithm for precise subject extraction.

This module provides the HybridWatermarkRemover class that uses:
1. Edge detection to identify the main subject (excluding watermarks)
2. Adaptive thresholding to separate subject from background
3. Morphological operations to remove edge artifacts
4. Smart background sampling (avoids rounded corners)

The result is a clean alpha mask where the subject is preserved and
everything else (including watermarks) becomes transparent.

Example usage:
    from icoft.core.watermark_advanced import HybridWatermarkRemover

    remover = HybridWatermarkRemover("input.png")
    result = remover.remove(threshold=30)
    result.save("output.png", "PNG")
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


class HybridWatermarkRemover:
    """
    Hybrid smart cutout algorithm for AI-generated logos.

    This algorithm is designed to extract the main subject from images
    with various backgrounds (dark, light, rounded corners) while
    automatically excluding watermarks and edge artifacts.
    """

    def __init__(self, image_path: str | Path):
        """
        Initialize the watermark remover.

        Args:
            image_path: Path to the input image file.
        """
        self.image_path = Path(image_path)
        self.image = Image.open(self.image_path).convert("RGB")
        self.img_array = np.array(self.image)
        self.bg_color = self._sample_background()

    def _sample_background(self) -> np.ndarray:
        """
        Sample background color from image edges.

        Samples from the middle 60% of each edge to avoid rounded corners.

        Returns:
            Median background color as RGB array.
        """
        h, w = self.img_array.shape[:2]
        edge = min(20, h // 10, w // 10)

        # Sample from middle 60% of each edge (avoid corners)
        samples = []
        # Top and bottom edges (middle 60%)
        samples.append(self.img_array[:edge, w // 5 : 4 * w // 5].reshape(-1, 3))
        samples.append(self.img_array[-edge:, w // 5 : 4 * w // 5].reshape(-1, 3))
        # Left and right edges (middle 60%)
        samples.append(self.img_array[h // 5 : 4 * h // 5, :edge].reshape(-1, 3))
        samples.append(self.img_array[h // 5 : 4 * h // 5, -edge:].reshape(-1, 3))

        all_samples = np.concatenate(samples)
        return np.median(np.asarray(all_samples), axis=0)

    def detect_subject_by_edges(self) -> np.ndarray:
        """
        Detect subject using edge detection (excludes watermarks).

        Returns:
            Binary mask of the subject (255 = subject, 0 = background).
        """
        gray = cv2.cvtColor(self.img_array, cv2.COLOR_RGB2GRAY)

        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Canny edge detection with adaptive thresholds
        median_val = np.median(blurred)
        sigma = 0.33
        lower = int(max(0, (1.0 - sigma) * median_val))
        upper = int(min(255, (1.0 + sigma) * median_val))

        edges = cv2.Canny(blurred, lower, upper)

        # Morphological operations to close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated_edges = cv2.dilate(edges, kernel, iterations=2)
        closed_edges = cv2.morphologyEx(dilated_edges, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create subject mask (fill all valid contours)
        subject_mask = np.zeros_like(closed_edges)

        if contours:
            total_area = self.img_array.shape[0] * self.img_array.shape[1]
            min_area = total_area * 0.0005

            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]

            # Smooth each contour with convex hull
            for contour in valid_contours:
                hull = cv2.convexHull(contour)
                cv2.drawContours(subject_mask, [hull], -1, 255, -1)

        return subject_mask

    def create_transparent_mask(self, subject_mask: np.ndarray, threshold: int = 30) -> np.ndarray:
        """
        Create alpha mask by removing background within subject area.

        Uses adaptive thresholding based on background brightness:
        - Dark backgrounds: brightness threshold + erosion (2px)
        - Light backgrounds: difference threshold + erosion (2px)

        Args:
            subject_mask: Binary mask from edge detection.
            threshold: Base threshold value (default: 30).

        Returns:
            Alpha mask (0-255) for transparency.
        """
        bg_brightness = np.mean(self.bg_color)

        if bg_brightness < 80:
            # Dark background: detect bright subject (white)
            brightness = np.mean(self.img_array[:, :, :3], axis=2)
            adaptive_threshold = bg_brightness + threshold * 3
            foreground_mask = (brightness > adaptive_threshold).astype(np.uint8) * 255

            # Erode 2px to remove dark edge artifacts
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            foreground_mask = cv2.erode(foreground_mask, kernel, iterations=2)

        else:
            # Light background: use difference threshold
            diff = np.sqrt(np.sum((self.img_array - self.bg_color) ** 2, axis=2))
            adaptive_threshold = threshold
            foreground_mask = (diff > adaptive_threshold).astype(np.uint8) * 255

            # Erode 2px to remove edge artifacts (same as dark background)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            foreground_mask = cv2.erode(foreground_mask, kernel, iterations=2)

        # Final alpha mask = subject AND foreground
        alpha_mask = cv2.bitwise_and(subject_mask, foreground_mask)

        # Morphological close to fill small holes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        alpha_mask = cv2.morphologyEx(alpha_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        # No Gaussian blur - we want clean edges for vectorization!
        # Blur would create semi-transparent gradients that confuse vectorizer
        return alpha_mask

    def remove(self, threshold: int = 30) -> Image.Image:
        """
        Remove background and watermarks using smart cutout.

        Args:
            threshold: Threshold value for detection (default: 30).

        Returns:
            RGBA image with transparent background.
        """
        # Step 1: Edge detection to identify subject
        subject_mask = self.detect_subject_by_edges()

        # Step 2: Create alpha mask (background becomes transparent)
        alpha_mask = self.create_transparent_mask(subject_mask, threshold=threshold)

        # Step 3: Create RGBA image
        rgba = np.dstack([self.img_array, alpha_mask])

        return Image.fromarray(rgba)

    def save(self, output_path: str | Path, threshold: int = 30) -> None:
        """
        Save the result to a PNG file.

        Args:
            output_path: Path to save the output file.
            threshold: Threshold value for detection (default: 30).
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = self.remove(threshold=threshold)
        result.save(output_path, "PNG")

        alpha = np.array(result)[:, :, 3]
        transparent = np.sum(alpha == 0)
        print(f"✓ {output_path.name}: 透明 {transparent / alpha.size * 100:.1f}%")
