# Icoft - Icon Forge

**From Single Image to Full-Platform App Icons**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.1--dev-blue.svg)](https://github.com/hexin/icoft)

Icoft is a command-line tool that converts a single image (PNG, JPG, JPEG, WEBP) into icons for all platforms (Windows, macOS, Linux, Web).

## Features

- **Step-by-Step Processing**: Unix-style composable parameters for precise control
- **Automatic Border Cropping**: Removes solid-color borders
- **Watermark/Noise Removal**: Extracts subject from background
- **Background to Transparent**: Converts single-color backgrounds to transparent
- **Vectorization**: PNG to SVG conversion with vtracer
- **Multi-Platform Support**:
  - **Windows**: `.ico` file (16, 24, 32, 48, 64, 128, 256 px)
  - **macOS**: `.icns` file + `icon_512x512.png`
  - **Linux**: PNG icon set following hicolor theme + SVG
  - **Web**: `favicon.ico`, PWA icons, `apple-touch-icon.png`
- **CLI Friendly**: Simple command-line interface with Rich output
- **Configurable**: Customizable thresholds, margins, and platform selection

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd icoft

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

```bash
# Basic usage (default: generate icons from original image)
icoft logo.png icons/

# With crop margin
icoft -m 10% logo.png icons/        # Crop + generate icons

# With custom parameters
icoft -m 10% -T 40 -B 15 logo.png out/

# Combined steps + icons (default)
icoft -m 10% -t logo.png icons/

# Specific step output (single file)
icoft -m 10% logo.png out.png --output=png
icoft -t logo.png out.png --output=png
icoft -s logo.png out.svg --output=svg
```

## Usage Examples

### Example 1: Convert AI Logo

```bash
# Generate logo from Midjourney/豆包
icoft my_logo.png output/
```

Output structure:
```
output/
├── windows/
│   └── app.ico
├── macos/
│   ├── app.icns (or icon_1024x1024.png)
│   └── icon_512x512.png
├── linux/
│   └── hicolor/
│       ├── 16x16/apps/app.png
│       ├── 32x32/apps/app.png
│       ├── ... (more sizes)
│       └── scalable/apps/app.svg
└── web/
    ├── favicon.ico
    ├── apple-touch-icon.png
    ├── icon-192x192.png
    ├── icon-512x512.png
    └── manifest.json
```

### Example 2: Python Package Integration

```bash
# In pyproject.toml
[tool.icoft]
source = "logo.png"
output = "package/icons/"

# Build icons
icoft --config=pyproject.toml
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/release.yml
- name: Generate icons
  run: |
    pip install icoft
    icoft logo.png resources/icons/
```

## Command-Line Options

```
Usage: icoft [OPTIONS] INPUT_FILE OUTPUT_DIR

Icoft - From Single Image to Full-Platform App Icons.

Processing Steps (can be combined):
  -m, --crop-margin       Crop borders with margin
  -T, --noise-threshold   Remove watermarks/noise
  -t, --transparent       Make background transparent
  -s, --svg               Vectorize to SVG

Output Options:
  --output=icon           Generate platform icons (default)
  --output=png            Save last processing step as PNG
  --output=svg            Save last processing step as SVG

Parameter Options:
  -m, --crop-margin=5%    Margin for cropping
  -T, --noise-threshold   Watermark removal sensitivity (default: 30)
  -B, --bg-threshold      Background threshold (default: 10)
  -S, --svg-speckle       Filter SVG noise (default: 10)
  -P, --svg-precision     SVG color precision (default: 6)

Options:
  -p, --platforms TEXT    Comma-separated platforms (default: all)
  --version               Show version
  -h, --help              Show help message
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run pyright .
```

### Project Structure

```
icoft/
├── src/icoft/
│   ├── cli.py              # CLI entry point
│   ├── core/
│   │   ├── processor.py    # Image preprocessing
│   │   └── generator.py    # Icon generation
│   └── platforms/          # Platform-specific modules
├── tests/
│   ├── test_cli.py
│   ├── test_processor.py
│   └── test_generator.py
├── docs/
└── examples/
```

## Roadmap

### v0.2.0-dev (Current)
- ✅ Unix-style CLI parameter design
- ✅ Step-by-step processing control
- ✅ Vectorization with vtracer
- ✅ Smart cutout improvements
- ✅ Edge artifact removal
- ✅ Configuration parameters with auto-enable

### v0.3.0 (Planned)
- [ ] Batch processing
- [ ] Configuration file support (YAML/JSON)
- [ ] Quality reports and recommendations
- [ ] Enhanced test coverage

### v1.0.0 (Future)
- [ ] iOS icon optimization
- [ ] Android adaptive icons
- [ ] CI/CD integration templates
- [ ] GUI application (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Image processing powered by [Pillow](https://pillow.readthedocs.io/) and [OpenCV](https://opencv.org/)
- Terminal output美化 with [Rich](https://rich.readthedocs.io/)

---

**Icoft** = **Icon** + **Forge** 🛠️

Made with ❤️ for developers everywhere
