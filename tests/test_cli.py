"""Tests for the CLI module."""

import pytest
from click.testing import CliRunner

from icoft.cli import main


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image."""
    from PIL import Image

    img_path = tmp_path / "test_logo.png"
    img = Image.new("RGBA", (200, 200), (255, 255, 255, 255))

    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (0, 0, 255, 255))

    img.save(img_path, "PNG")
    return img_path


class TestCLI:
    """Test cases for CLI commands."""

    def test_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Icoft" in result.output
        assert "SOURCE_FILE" in result.output
        assert "DEST_DIR" in result.output

    def test_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.5" in result.output

    def test_basic_conversion(self, sample_image, tmp_path):
        """Test basic icon conversion."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        result = runner.invoke(main, [str(sample_image), str(output_dir)])

        assert result.exit_code == 0

        assert (output_dir / "windows" / "app.ico").exists()
        assert (output_dir / "macos" / "icon_512x512.png").exists()
        assert (output_dir / "web" / "favicon.ico").exists()

    def test_specific_platforms(self, sample_image, tmp_path):
        """Test conversion with specific platforms."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        result = runner.invoke(
            main,
            [str(sample_image), str(output_dir), "--platforms", "windows,web"],
        )

        assert result.exit_code == 0

        assert (output_dir / "windows" / "app.ico").exists()
        assert (output_dir / "web" / "favicon.ico").exists()
        assert not (output_dir / "macos").exists()

    def test_custom_margin(self, sample_image, tmp_path):
        """Test conversion with custom margin."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        result = runner.invoke(
            main,
            [str(sample_image), str(output_dir), "-c", "5%"],
        )

        assert result.exit_code == 0

    def test_no_crop(self, sample_image, tmp_path):
        """Test conversion without cropping (default behavior)."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        # Default behavior: no processing, just generate icons from original
        result = runner.invoke(
            main,
            [str(sample_image), str(output_dir)],
        )

        assert result.exit_code == 0

    def test_no_transparent(self, sample_image, tmp_path):
        """Test conversion without transparent background (default behavior)."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        # Default behavior: no processing steps enabled
        result = runner.invoke(
            main,
            [str(sample_image), str(output_dir)],
        )

        assert result.exit_code == 0

    def test_file_not_found(self, tmp_path):
        """Test error handling for non-existent file."""
        runner = CliRunner()
        output_dir = tmp_path / "icons"

        result = runner.invoke(main, ["/nonexistent/file.png", str(output_dir)])

        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output.lower()
