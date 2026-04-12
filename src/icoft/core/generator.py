"""Icon generator module for Icoft."""

import io
from pathlib import Path

from PIL import Image


class IconGenerator:
    """
    Icon generator for multiple platforms.

    Generates icons in various formats for Windows, macOS, Linux, and Web.
    """

    def __init__(self, image: Image.Image, output_dir: str | Path) -> None:
        """
        Initialize the icon generator.

        Args:
            image: PIL Image object (should be RGBA mode).
            output_dir: Output directory for generated icons.
        """
        self.image = image.convert("RGBA")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_windows(self) -> None:
        """
        Generate Windows .ico file with multiple resolutions.

        Creates an .ico file containing icons at 16, 24, 32, 48, 64, 128, and 256 pixels.
        """
        output_path = self.output_dir / "windows"
        output_path.mkdir(parents=True, exist_ok=True)

        ico_path = output_path / "app.ico"

        sizes = [16, 24, 32, 48, 64, 128, 256]
        icons = []

        for size in sizes:
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            if size < 64:
                from PIL import ImageFilter

                if size < 32:
                    sharpness = 180
                elif size < 48:
                    sharpness = 150
                else:
                    sharpness = 130
                resized = resized.filter(
                    ImageFilter.UnsharpMask(radius=1, percent=sharpness, threshold=3)
                )

            icons.append(resized)

        icons[0].save(
            ico_path,
            format="ICO",
            sizes=[(size, size) for size in sizes],
            append_images=icons[1:],
        )

    def generate_macos(self) -> None:
        """
        Generate macOS .icns file and icon_512x512.png.

        Creates an .icns file and a 512x512 PNG for App Store submission.
        """
        output_path = self.output_dir / "macos"
        output_path.mkdir(parents=True, exist_ok=True)

        png_512 = output_path / "icon_512x512.png"
        resized_512 = self.image.resize((512, 512), Image.Resampling.LANCZOS)
        resized_512.save(png_512, "PNG")

        icns_path = output_path / "app.icns"

        try:
            import importlib.util

            if importlib.util.find_spec("PIL.IcnsImagePlugin"):
                self.image.save(icns_path, format="ICNS")
            else:
                raise ImportError("ICNS support not available")
        except (ImportError, OSError):
            png_1024 = output_path / "icon_1024x1024.png"
            resized_1024 = self.image.resize((1024, 1024), Image.Resampling.LANCZOS)
            resized_1024.save(png_1024, "PNG")

    def generate_linux(self) -> None:
        """
        Generate Linux icon set in hicolor theme format.

        Creates PNG icons at standard sizes following the hicolor icon theme specification.
        """
        output_path = self.output_dir / "linux" / "hicolor"

        sizes = [16, 22, 24, 32, 36, 48, 64, 72, 96, 128, 256, 512]

        for size in sizes:
            size_dir = output_path / f"{size}x{size}" / "apps"
            size_dir.mkdir(parents=True, exist_ok=True)

            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            if size < 64:
                from PIL import ImageFilter

                if size < 32:
                    sharpness = 180
                elif size < 48:
                    sharpness = 150
                else:
                    sharpness = 130
                resized = resized.filter(
                    ImageFilter.UnsharpMask(radius=1, percent=sharpness, threshold=3)
                )

            icon_path = size_dir / "app.png"
            resized.save(icon_path, "PNG")

        svg_dir = output_path / "scalable" / "apps"
        svg_dir.mkdir(parents=True, exist_ok=True)

        svg_path = svg_dir / "app.svg"
        self._generate_svg(svg_path)

    def generate_web(self) -> None:
        """
        Generate web icons including favicon and PWA icons.

        Creates favicon.ico, apple-touch-icon.png, and various PWA icon sizes.
        """
        output_path = self.output_dir / "web"
        output_path.mkdir(parents=True, exist_ok=True)

        favicon_sizes = [16, 32]
        favicon_icons = []

        for size in favicon_sizes:
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)
            favicon_icons.append(resized)

        favicon_path = output_path / "favicon.ico"
        favicon_icons[0].save(
            favicon_path,
            format="ICO",
            sizes=[(size, size) for size in favicon_sizes],
            append_images=favicon_icons[1:],
        )

        apple_touch_path = output_path / "apple-touch-icon.png"
        apple_touch = self.image.resize((180, 180), Image.Resampling.LANCZOS)
        apple_touch.save(apple_touch_path, "PNG")

        pwa_sizes = [192, 512]
        for size in pwa_sizes:
            pwa_path = output_path / f"icon-{size}x{size}.png"
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(pwa_path, "PNG")

        favicon_sizes = [16, 32]
        for i, size in enumerate(favicon_sizes):
            if size < 64:
                from PIL import ImageFilter

                sharpness = 180 if size < 32 else 150
                favicon_icons[i] = favicon_icons[i].filter(
                    ImageFilter.UnsharpMask(radius=1, percent=sharpness, threshold=3)
                )

        manifest_path = output_path / "manifest.json"
        self._generate_manifest(manifest_path)

    def _generate_svg(self, output_path: Path) -> None:
        """
        Generate SVG version of the icon.

        Args:
            output_path: Path to save the SVG file.
        """
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <image href="data:image/png;base64,{self._image_to_base64()}" width="512" height="512"/>
</svg>"""

        output_path.write_text(svg_content, encoding="utf-8")

    def _generate_manifest(self, output_path: Path) -> None:
        """
        Generate PWA manifest.json file.

        Args:
            output_path: Path to save the manifest file.
        """
        import json

        manifest = {
            "icons": [
                {
                    "src": "icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ]
        }

        output_path.write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )

    def _image_to_base64(self) -> str:
        """
        Convert current image to base64 encoded string.

        Returns:
            Base64 encoded PNG image string.
        """
        import base64

        buffer = io.BytesIO()
        self.image.save(buffer, format="PNG")
        buffer.seek(0)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode("utf-8")
