# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-04-14

### Removed
- RMBG-1.4 model support (removed due to quality issues)
- CLI options: `--ai-model`, `--ai-threshold`, `--ai-denoise`, `--hole-fill`, `--hole-fill-threshold`
- All RMBG-related test scripts in `scripts/` directory

### Changed
- Simplified AI background removal to use only U²-Net model
- Improved CLI help text organization (alphabetical order for options)
- Removed step numbers from processing output
- Updated command description to mention `-o` option for intermediate output

## [0.3.3] - 2026-04-14

### Removed
- Unused dependencies: `opencv-python`, `scipy`, `scikit-image`
- These were legacy dependencies from previous watermark removal algorithm

### Changed
- Streamlined dependency tree for faster installation and smaller package size

## [0.3.2] - 2026-04-14

### Fixed
- Fix linter warnings for unused cairosvg imports
- Use `importlib.util.find_spec()` for module availability checks
- Add None check for cairosvg.svg2png return value
- Fix import ordering in generator.py

## [0.3.1] - 2026-04-13

### Fixed
- Use source filename for output files instead of hardcoded names (e.g., `cogist17.svg` instead of `04_vectorized.svg`)
- Replace `open()` with `Path.open()` (PTH123)
- Add `strict=True` to `zip()` calls (B905)
- Fix type checking issues (crop_margin None type, vtracer imports)

### Removed
- Unused `import struct` in generator.py

## [0.3.0] - 2026-04-12

### Added
- Full Windows 10/11 ICO support (8 sizes: 16-256px with PNG compression)
- Complete macOS Retina ICNS support (10 PNG sizes + ICNS container)
- Official Linux hicolor specification compliance (8 sizes + SVG)
- Single file output mode (`-o png` / `-o svg`)
- Platform names in `--platforms` help text
- Clear error messages for missing arguments

### Changed
- Linux icon sizes to official hicolor spec (removed Android sizes, added 256px)
- Output directory structure documentation with complete file listing
- `--output` help text to clarify directory vs single file modes
- CLI examples to use short parameter `-o`

### Removed
- Complex watermark removal algorithm (`HybridWatermarkRemover`)
- `-T/--noise-threshold` parameter (smart cutout)
- `denoise()` method and OpenCV dependency for watermark removal
- Unrealistic v0.3 roadmap items (batch processing, config files)

### Fixed
- Windows ICO generation (Pillow bug - manual implementation)
- macOS ICNS generation (manual implementation with OSType codes)
- Missing 256px size in Linux icon set
- Unclear platform parameter names
- Added `--output=svg` option to save processing result as single SVG
- Updated CLI help and documentation with new output parameter design

### Removed
- `-i, --icon` parameter (replaced by `--output=icon`)
- `-c, --crop` parameter (use `-m/--crop-margin` with explicit value)
- `-u, --cutout` parameter (functionality merged into noise removal workflow)
- `-I, --output-intermediate` parameter (redundant with `--output=png`)
- `--preset` parameter (users can combine parameters directly)

### Fixed
- Default behavior now correctly generates icons when no parameters specified
- Parameter logic simplified: configuration parameters auto-enable corresponding steps

## [0.2.0] - 2026-04-12

### Added
- Unix-style CLI parameter design with composable short options (`-c`, `-u`, `-t`, `-s`, `-i`)
- Step control parameters:
  - `-c, --crop`: Crop borders
  - `-u, --cutout`: Smart cutout to extract subject
  - `-t, --transparent`: Make background transparent
  - `-s, --svg`: Vectorize PNG to SVG
  - `-i, --icon`: Generate platform icons (default)
- Configuration parameters with auto-enable:
  - `-m, --crop-margin`: Custom crop margin (default: 5%)
  - `-T, --cutout-threshold`: Smart cutout sensitivity (0-255, default: 30)
  - `-B, --bg-threshold`: Background removal tolerance (0-255, default: 10)
  - `-S, --svg-speckle`: Filter SVG noise (default: 10)
  - `-P, --svg-precision`: SVG color precision (default: 6)
- Preset configurations: `--preset=minimal|standard|full|icon`
- Intermediate output option: `-I, --output-intermediate`
- Vectorization support with vtracer library
- SVG background rendering with CairoSVG

### Changed
- **Breaking**: CLI parameter order changed to Unix convention (options first)
- Removed `--mode` parameter (replaced by step parameter combinations)
- Default output behavior: last step determines output type
- Improved edge artifact removal in smart cutout (erosion for both dark and light backgrounds)
- Removed Gaussian blur from watermark removal to improve vectorization quality

### Removed
- `--smooth-edges` option (redundant with vectorization)
- `smooth_edges()` method from processor
- Redundant anti-aliasing code

### Fixed
- Edge artifacts in smart cutout for light backgrounds
- Black dots in vectorized output (adjusted filter_speckle to 10)
- SVG background rectangle insertion order

## [0.1.0] - 2026-04-11

### Added
- Initial release
- Core image processing:
  - Automatic border cropping
  - Background to transparent conversion
  - Smart cutout (HybridWatermarkRemover algorithm)
- Multi-platform icon generation:
  - Windows: `.ico` file (16-256 px)
  - macOS: `.icns` + `icon_512x512.png`
  - Linux: PNG icon set (hicolor theme) + SVG
  - Web: favicon, PWA icons, manifest.json
- CLI interface with Click and Rich
- Configuration options: `--margin`, `--platforms`, `--no-crop`, `--no-transparent`
- Comprehensive test suite (23 tests)
- Documentation: README.md, project status, design philosophy

[Unreleased]: https://github.com/hexin/icoft/compare/v0.2.2-dev...HEAD
[0.2.2-dev]: https://github.com/hexin/icoft/compare/v0.2.1-dev...v0.2.2-dev
[0.2.1-dev]: https://github.com/hexin/icoft/compare/v0.2.0...v0.2.1-dev
[0.2.0]: https://github.com/hexin/icoft/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hexin/icoft/releases/tag/v0.1.0
