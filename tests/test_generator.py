"""Tests for the IconGenerator class."""

import json

import pytest
from PIL import Image

from icoft.core.generator import IconGenerator


@pytest.fixture
def sample_icon_image():
    """Create a sample icon image for testing."""
    img = Image.new("RGBA", (512, 512), (255, 0, 0, 255))

    for x in range(100, 412):
        for y in range(100, 412):
            img.putpixel((x, y), (0, 255, 0, 255))

    return img


@pytest.fixture
def generator(sample_icon_image, tmp_path):
    """Create an IconGenerator instance."""
    output_dir = tmp_path / "icons"
    return IconGenerator(sample_icon_image, output_dir)


class TestIconGenerator:
    """Test cases for IconGenerator."""

    def test_init(self, sample_icon_image, tmp_path):
        """Test generator initialization."""
        output_dir = tmp_path / "icons"
        generator = IconGenerator(sample_icon_image, output_dir)

        assert generator.image.mode == "RGBA"
        assert generator.output_dir == output_dir

    def test_generate_windows(self, generator):
        """Test Windows icon generation."""
        generator.generate_windows()

        ico_path = generator.output_dir / "windows" / "app.ico"
        assert ico_path.exists()

        ico = Image.open(ico_path)
        assert ico.format == "ICO"

    def test_generate_macos(self, generator):
        """Test macOS icon generation."""
        generator.generate_macos()

        macos_dir = generator.output_dir / "macos"
        png_512 = macos_dir / "icon_512x512.png"

        assert png_512.exists()

        img = Image.open(png_512)
        assert img.size == (512, 512)

    def test_generate_linux(self, generator):
        """Test Linux icon generation."""
        generator.generate_linux()

        linux_dir = generator.output_dir / "linux" / "hicolor"

        # Official hicolor specification sizes
        sizes = [16, 22, 24, 32, 48, 64, 128, 256]
        for size in sizes:
            icon_path = linux_dir / f"{size}x{size}" / "apps" / "app.png"
            assert icon_path.exists()

            img = Image.open(icon_path)
            assert img.size == (size, size)

        svg_path = linux_dir / "scalable" / "apps" / "app.svg"
        assert svg_path.exists()

    def test_generate_web(self, generator):
        """Test web icon generation."""
        generator.generate_web()

        web_dir = generator.output_dir / "web"

        favicon_path = web_dir / "favicon.ico"
        assert favicon_path.exists()

        apple_touch_path = web_dir / "apple-touch-icon.png"
        assert apple_touch_path.exists()

        img = Image.open(apple_touch_path)
        assert img.size == (180, 180)

        pwa_192 = web_dir / "icon-192x192.png"
        assert pwa_192.exists()

        pwa_512 = web_dir / "icon-512x512.png"
        assert pwa_512.exists()

        manifest_path = web_dir / "manifest.json"
        assert manifest_path.exists()

        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(manifest_text)

        assert "icons" in manifest
        assert len(manifest["icons"]) == 2

    def test_multiple_platforms(self, sample_icon_image, tmp_path):
        """Test generating icons for multiple platforms."""
        output_dir = tmp_path / "multi_icons"
        generator = IconGenerator(sample_icon_image, output_dir)

        generator.generate_windows()
        generator.generate_macos()
        generator.generate_web()

        assert (output_dir / "windows" / "app.ico").exists()
        assert (output_dir / "macos" / "icon_512x512.png").exists()
        assert (output_dir / "web" / "favicon.ico").exists()
