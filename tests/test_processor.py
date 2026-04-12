"""Tests for the ImageProcessor class."""

import numpy as np
import pytest
from PIL import Image

from icoft.core.processor import ImageProcessor


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image with a border."""
    img_path = tmp_path / "test_image.png"

    img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))

    for x in range(20, 80):
        for y in range(20, 80):
            img.putpixel((x, y), (255, 0, 0, 255))

    img.save(img_path, "PNG")
    return img_path


@pytest.fixture
def transparent_image(tmp_path):
    """Create a sample image with transparent background."""
    img_path = tmp_path / "test_transparent.png"

    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))

    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (0, 255, 0, 255))

    img.save(img_path, "PNG")
    return img_path


class TestImageProcessor:
    """Test cases for ImageProcessor."""

    def test_init(self, sample_image):
        """Test processor initialization."""
        processor = ImageProcessor(sample_image)
        assert processor.image is not None
        assert processor.image.mode == "RGBA"

    def test_crop_borders(self, sample_image):
        """Test border cropping functionality."""
        processor = ImageProcessor(sample_image)
        original_size = processor.image.size

        processor.crop_borders(margin="0%")

        assert processor.image.size[0] <= original_size[0]
        assert processor.image.size[1] <= original_size[1]

    def test_crop_borders_with_margin(self, sample_image):
        """Test cropping with margin percentage."""
        processor = ImageProcessor(sample_image)

        processor.crop_borders(margin="10%")

        width, height = processor.image.size
        assert width > 0
        assert height > 0

    def test_make_background_transparent(self, sample_image):
        """Test background to transparent conversion."""
        processor = ImageProcessor(sample_image)

        processor.make_background_transparent(tolerance=20)

        img_array = np.array(processor.image)
        corner_alpha = img_array[0, 0, 3]
        assert corner_alpha == 0

    def test_resize(self, sample_image):
        """Test image resizing."""
        processor = ImageProcessor(sample_image)

        processor.resize((50, 50))

        assert processor.image.size == (50, 50)

    def test_save(self, sample_image, tmp_path):
        """Test image saving."""
        processor = ImageProcessor(sample_image)
        output_path = tmp_path / "output.png"

        processor.save(output_path)

        assert output_path.exists()

        saved_img = Image.open(output_path)
        assert saved_img.mode == "RGBA"

    def test_chain_operations(self, sample_image):
        """Test chaining multiple operations."""
        processor = ImageProcessor(sample_image)

        processor.crop_borders(margin="5%").resize((64, 64))

        assert processor.image.size == (64, 64)

    def test_parse_margin_percentage(self, sample_image):
        """Test margin parsing with percentage."""
        processor = ImageProcessor(sample_image)

        margin = processor._parse_margin("10%", (100, 100))
        assert margin == 10

        margin = processor._parse_margin("20%", (200, 200))
        assert margin == 40

    def test_parse_margin_pixels(self, sample_image):
        """Test margin parsing with pixel values."""
        processor = ImageProcessor(sample_image)

        margin = processor._parse_margin("10px", (100, 100))
        assert margin == 10

        margin = processor._parse_margin("5px", (100, 100))
        assert margin == 5
