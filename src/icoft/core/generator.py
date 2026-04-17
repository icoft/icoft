"""Icon generator module for Icoft."""

import io
import struct
from pathlib import Path

from PIL import Image


class IconGenerator:
    """
    Icon generator for multiple platforms.

    Generates icons in various formats for Windows, macOS, Linux, Web, iOS, and Android.
    """

    def __init__(
        self, image: Image.Image, output_dir: str | Path, svg_content: str | None = None
    ) -> None:
        """
        Initialize the icon generator.

        Args:
            image: PIL Image object (should be RGBA mode).
            output_dir: Output directory for generated icons.
            svg_content: Optional SVG string for high-quality vector-based scaling.
        """
        self.image = image.convert("RGBA")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.svg_content = svg_content
        self._check_vector_support()

    def _check_vector_support(self) -> bool:
        """Check if cairosvg is available for vector-based rendering."""
        import importlib.util

        self.has_vector_support = importlib.util.find_spec("cairosvg") is not None
        return self.has_vector_support

    def _render_from_svg(self, size: int) -> Image.Image:
        """
        Render a specific size from SVG content using cairosvg.

        Args:
            size: The target width/height in pixels.

        Returns:
            Resized PIL Image.
        """
        if not self.svg_content or not self.has_vector_support:
            # Fallback to standard resizing
            return self.image.resize((size, size), Image.Resampling.LANCZOS)

        try:
            import io

            import cairosvg  # type: ignore[import-untyped]

            png_data = cairosvg.svg2png(
                bytestring=self.svg_content.encode("utf-8"),
                output_width=size,
                output_height=size,
            )
            if png_data is None:
                raise ValueError("cairosvg.svg2png returned None")
            return Image.open(io.BytesIO(png_data)).convert("RGBA")
        except Exception:
            # If rendering fails, fallback to standard resizing
            return self.image.resize((size, size), Image.Resampling.LANCZOS)

    def generate_windows(self) -> None:
        """
        Generate Windows .ico file with full resolution support.

        Creates an .ico file containing icons at:
        16, 20, 24, 32, 40, 48, 64, 256 pixels (Windows 10/11 compliant)
        All sizes use 32-bit ARGB with PNG compression for 256x256.
        """
        import io

        output_path = self.output_dir / "windows"
        output_path.mkdir(parents=True, exist_ok=True)

        ico_path = output_path / "app.ico"

        # Full Windows 10/11 specification sizes
        # 16/20/24/32/40/48/64 for various DPI settings
        # 256 for high-DPI displays and modern UI
        sizes = [16, 20, 24, 32, 40, 48, 64, 256]

        # Create PNG data for each size
        png_data = []
        for size in sizes:
            resized = self._render_from_svg(size)

            # Apply sharpening for small sizes (only if not using vector rendering)
            if size < 64 and not (self.svg_content and self.has_vector_support):
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

            # Save as PNG bytes
            buffer = io.BytesIO()
            resized.save(buffer, format="PNG")
            png_data.append(buffer.getvalue())

        # Generate ICO file manually (Pillow has bugs with multi-size ICO)
        ico_data = self._create_ico_from_png(png_data, sizes)

        # Save ICO file
        with ico_path.open("wb") as f:
            f.write(ico_data)

    def _create_ico_from_png(self, png_images: list[bytes], sizes: list[int]) -> bytes:
        """
        Create ICO file from PNG data.

        Args:
            png_images: List of PNG image data (bytes)
            sizes: List of sizes corresponding to each PNG

        Returns:
            ICO file data (bytes)
        """
        # ICO header: reserved(2) + type(2) + count(2)
        header = struct.pack("<HHH", 0, 1, len(png_images))

        # Icon directory entries
        icon_dir = b""
        offset = 6 + 16 * len(png_images)  # Header + directory size

        for png_data, size in zip(png_images, sizes, strict=True):
            png_size = len(png_data)

            # ICO entry: width, height, colors, reserved, planes, bpp, size, offset
            # width/height of 0 means 256
            w = 0 if size == 256 else size
            h = 0 if size == 256 else size

            entry = struct.pack(
                "<BBBBHHII",
                w,
                h,
                0,
                0,  # width, height, colors, reserved
                1,
                32,  # planes, bpp (32-bit)
                png_size,  # size of PNG data
                offset,  # offset to PNG data
            )
            icon_dir += entry
            offset += png_size

        # Combine all parts
        ico_data = header + icon_dir
        for png in png_images:
            ico_data += png

        return ico_data

    def _create_icns_from_png(self, png_icons: list[tuple[int, Image.Image]]) -> bytes:
        """
        Create ICNS file from PNG images.

        ICNS format uses OSType codes to identify icon types:
        - ic07: 128x128 @1x
        - ic08: 128x128 @2x (256x256)
        - ic09: 512x512 @1x
        - ic10: 512x512 @2x (1024x1024)
        - ic11: 16x16 @1x
        - ic12: 16x16 @2x (32x32)
        - ic13: 32x32 @1x
        - ic14: 32x32 @2x (64x64)

        Args:
            png_icons: List of (size, Image) tuples

        Returns:
            ICNS file data (bytes)
        """
        # Map sizes to ICNS icon types
        icon_types = {
            16: b"ic11",  # 16x16 @1x
            32: b"ic12",  # 16x16 @2x or 32x32 @1x
            64: b"ic14",  # 32x32 @2x
            128: b"ic07",  # 128x128 @1x
            256: b"ic08",  # 128x128 @2x or 256x256 @1x
            512: b"ic09",  # 256x256 @2x or 512x512 @1x
            1024: b"ic10",  # 512x512 @2x
        }

        # Generate PNG data for each size
        icon_data = []
        for size, image in png_icons:
            if size in icon_types:
                # Save image as PNG
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                png_data = buffer.getvalue()

                icon_type = icon_types[size]
                icon_data.append((icon_type, png_data))

        # ICNS header: 'icns' (4) + size (4) + 'big' endian
        # Total size = 8 (header) + sum of all icon sizes
        total_size = 8
        for _, data in icon_data:
            total_size += 8 + len(data)  # type(4) + size(4) + data

        header = struct.pack(">4sI", b"icns", total_size)

        # Icon elements
        elements = b""
        for icon_type, png_data in icon_data:
            # Element header: type (4) + size (4, including header)
            element_size = 8 + len(png_data)
            element_header = struct.pack(">4sI", icon_type, element_size)
            elements += element_header + png_data

        return header + elements

    def generate_macos(self) -> None:
        """
        Generate macOS .icns file with full Retina support.

        Creates an .icns file containing all required sizes:
        16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
        Plus individual PNG files for App Store submission.
        """
        output_path = self.output_dir / "macos"
        output_path.mkdir(parents=True, exist_ok=True)

        # Full macOS specification sizes (includes 1x and @2x Retina)
        # Based on point sizes: 16pt, 32pt, 128pt, 256pt, 512pt
        png_files = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]

        # Generate all PNG files and collect for ICNS
        png_icons = []
        for size, filename in png_files:
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            # Save PNG
            png_path = output_path / filename
            resized.save(png_path, "PNG")

            # Collect unique sizes for ICNS
            if size not in [p[0] for p in png_icons]:
                png_icons.append((size, resized))

        # Generate ICNS file manually with all sizes
        icns_path = output_path / "app.icns"
        icns_data = self._create_icns_from_png(png_icons)

        with icns_path.open("wb") as f:
            f.write(icns_data)

    def generate_linux(self) -> None:
        """
        Generate Linux icon set following freedesktop.org hicolor specification.

        Creates PNG icons at standard sizes + SVG vector for infinite scalability.
        Directory structure: hicolor/SIZExSIZE/apps/app.png
        """
        output_path = self.output_dir / "linux" / "hicolor"

        # Official hicolor specification sizes (real pixels, no 1x/@2x concept)
        # Minimum compliant: 16, 32, 48, 64, 128 + scalable/SVG
        # Full specification includes all common sizes
        sizes = [16, 22, 24, 32, 48, 64, 128, 256]

        for size in sizes:
            size_dir = output_path / f"{size}x{size}" / "apps"
            size_dir.mkdir(parents=True, exist_ok=True)

            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            # Apply sharpening for small sizes (better clarity)
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

        # Generate SVG vector icon (preferred format - scales to any size)
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
        # iOS doesn't support transparency, convert to RGB
        if apple_touch.mode == "RGBA":
            # Create white background and composite
            background = Image.new("RGB", apple_touch.size, (255, 255, 255))
            background.paste(apple_touch, mask=apple_touch.split()[3])
            apple_touch = background
        else:
            apple_touch = apple_touch.convert("RGB")
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

    def generate_ios(self) -> None:
        """
        Generate iOS icon set for App Store and device usage.

        Creates icons in the required sizes for iPhone, iPad, and App Store.
        All icons are RGB mode (no alpha channel) as per iOS requirements.
        Directory structure: ios/AppIcon.appiconset/
        """
        output_path = self.output_dir / "ios" / "AppIcon.appiconset"
        output_path.mkdir(parents=True, exist_ok=True)

        # iOS icon specifications (all must be RGB, no transparency)
        # Format: (size, scale, filename, idiom)
        icon_specs = [
            # iPhone/iPad notification icons (20pt)
            (40, "@2x", "Icon-Notification-20@2x.png", "iphone"),
            (60, "@3x", "Icon-Notification-20@3x.png", "iphone"),
            # iPhone/iPad settings icons (29pt)
            (58, "@2x", "Icon-Settings-29@2x.png", "iphone"),
            (87, "@3x", "Icon-Settings-29@3x.png", "iphone"),
            # iPhone Spotlight icons (40pt)
            (80, "@2x", "Icon-Spotlight-40@2x.png", "iphone"),
            (120, "@3x", "Icon-Spotlight-40@3x.png", "iphone"),
            # iPhone app icons (60pt)
            (120, "@2x", "Icon-App-60@2x.png", "iphone"),
            (180, "@3x", "Icon-App-60@3x.png", "iphone"),
            # iPad Spotlight icons (40pt)
            (80, "@2x", "Icon-Spotlight-40-iPad@2x.png", "ipad"),
            # iPad app icons (76pt)
            (76, "@1x", "Icon-App-76@1x.png", "ipad"),
            (152, "@2x", "Icon-App-76@2x.png", "ipad"),
            # iPad Pro app icons (83.5pt)
            (167, "@2x", "Icon-App-83.5@2x.png", "ipad"),
            # App Store icon (required)
            (1024, "@1x", "Icon-AppStore-1024@1x.png", "ios-marketing"),
        ]

        # Generate all icons
        for size, _scale, filename, _idiom in icon_specs:
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            # iOS requires RGB mode (no alpha channel)
            if resized.mode == "RGBA":
                # Create white background and composite
                background = Image.new("RGB", resized.size, (255, 255, 255))
                background.paste(resized, mask=resized.split()[3])
                resized = background
            else:
                resized = resized.convert("RGB")

            icon_path = output_path / filename
            resized.save(icon_path, "PNG")

        # Generate Contents.json for Asset Catalog
        contents = {
            "images": [],
            "info": {"version": 1, "author": "icoft"},
        }

        # Map filenames to Contents.json entries
        for size, scale, filename, idiom in icon_specs:
            # Calculate point size correctly
            if size == 167:  # 83.5pt @2x
                size_in_points = 83.5
            elif scale == "@1x":
                size_in_points = size
            elif scale == "@2x":
                size_in_points = size // 2
            elif scale == "@3x":
                size_in_points = size // 3
            else:
                size_in_points = size

            entry = {
                "idiom": idiom,
                "filename": filename,
            }

            # Add size field (except for marketing icon)
            if idiom != "ios-marketing":
                # Format size with .5 if needed
                if isinstance(size_in_points, float):
                    entry["size"] = f"{size_in_points}x{size_in_points}"
                else:
                    entry["size"] = f"{size_in_points}x{size_in_points}"
                entry["scale"] = scale.replace("@", "").replace("x", "x")
            else:
                entry["size"] = "1024x1024"

            contents["images"].append(entry)

        contents_path = output_path / "Contents.json"
        import json

        contents_path.write_text(json.dumps(contents, indent=2), encoding="utf-8")

    def generate_android(self) -> None:
        """
        Generate Android adaptive icon set.

        Creates foreground and background layers for adaptive icons,
        plus legacy icons for older Android versions.
        Directory structure: android/res/mipmap-*/
        """

        output_path = self.output_dir / "android"
        output_path.mkdir(parents=True, exist_ok=True)

        # Android density buckets with corresponding sizes
        densities = [
            ("mdpi", 48),  # 1x baseline
            ("hdpi", 72),  # 1.5x
            ("xhdpi", 96),  # 2x
            ("xxhdpi", 144),  # 3x
            ("xxxhdpi", 192),  # 4x
        ]

        # Google Play Store icon
        play_store_size = 512
        play_store_path = output_path / "playstore-icon.png"
        play_store_icon = self.image.resize(
            (play_store_size, play_store_size), Image.Resampling.LANCZOS
        )
        play_store_icon.save(play_store_path, "PNG")

        # Generate adaptive icons for each density
        for density_name, size in densities:
            density_dir = output_path / "res" / f"mipmap-{density_name}"
            density_dir.mkdir(parents=True, exist_ok=True)

            # Resize image
            resized = self.image.resize((size, size), Image.Resampling.LANCZOS)

            # For adaptive icons, we need separate foreground and background
            # Foreground: the actual icon content (with safe zone consideration)
            # Background: can be solid color or extracted from image

            # Create foreground (centered with padding for safe zone)
            # Android adaptive icons have a safe zone of 66% (33% padding on each side)
            safe_zone = int(size * 0.66)
            offset = (size - safe_zone) // 2

            # Extract center portion for foreground
            foreground = resized.crop((offset, offset, offset + safe_zone, offset + safe_zone))
            foreground = foreground.resize((size, size), Image.Resampling.LANCZOS)

            # Create simple background (white by default, could be customized)
            background = Image.new("RGBA", (size, size), (255, 255, 255, 255))

            # Save foreground and background
            fg_path = density_dir / "ic_launcher_foreground.png"
            bg_path = density_dir / "ic_launcher_background.png"

            foreground.save(fg_path, "PNG")
            background.save(bg_path, "PNG")

            # Also save legacy icon (combined) for older Android versions
            legacy_path = density_dir / "ic_launcher.png"
            resized.save(legacy_path, "PNG")

            # Round icon for Android 7.1+
            round_path = density_dir / "ic_launcher_round.png"
            resized.save(round_path, "PNG")

        # Generate adaptive icon XML resources
        res_xml_dir = output_path / "res" / "mipmap-anydpi-v26"
        res_xml_dir.mkdir(parents=True, exist_ok=True)

        # ic_launcher.xml
        launcher_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>"""

        launcher_path = res_xml_dir / "ic_launcher.xml"
        launcher_path.write_text(launcher_xml, encoding="utf-8")

        # ic_launcher_round.xml
        launcher_round_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>"""

        launcher_round_path = res_xml_dir / "ic_launcher_round.xml"
        launcher_round_path.write_text(launcher_round_xml, encoding="utf-8")

        # Generate AndroidManifest.xml snippet
        manifest_snippet = """<!-- Add these lines to your AndroidManifest.xml -->
<application
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    ... >
</application>"""

        manifest_path = output_path / "AndroidManifest-snippet.xml"
        manifest_path.write_text(manifest_snippet, encoding="utf-8")

        # Generate README with instructions
        readme_content = """# Android Icon Set

This directory contains Android adaptive icons generated by Icoft.

## Structure

- `res/mipmap-*/`: Density-specific icon resources
- `res/mipmap-anydpi-v26/`: Adaptive icon XML definitions (Android 8.0+)
- `playstore-icon.png`: 512x512 icon for Google Play Store

## Installation

1. Copy the `res` directory to your Android project's `app/src/main/` directory
2. Update your `AndroidManifest.xml` to reference the icons (see AndroidManifest-snippet.xml)
3. Upload `playstore-icon.png` to Google Play Console

## Notes

- Adaptive icons require Android 8.0 (API 26) or higher
- Legacy icons are included for backward compatibility
- The foreground layer uses a 66% safe zone as recommended by Android guidelines
"""

        readme_path = output_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

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
            "name": "Application",
            "short_name": "App",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
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
            ],
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
