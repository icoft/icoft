# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- CLI parameter order to follow Unix conventions: `icoft [OPTIONS] INPUT_FILE OUTPUT_DIR`
- Default behavior: no arguments shows help message

## [0.2.1-dev] - 2026-04-12

### Changed
- Replaced `-i, --icon` flag with `--output` parameter for better output control
- Simplified CLI parameters: removed `-c/--crop`, `-u/--cutout`, and `-I/--output-intermediate`
- Renamed `-T/--cutout-threshold` to `-T/--noise-threshold` (watermark/noise removal)
- Default output behavior: `--output=icon` (generates full platform icon set)
- Added `--output=png` option to save processing result as single PNG
- Added `--output=svg` option to save processing result as single SVG
- Updated CLI help and documentation with new output parameter design

### Removed
- `-i, --icon` parameter (replaced by `--output=icon`)
- `-c, --crop` parameter (use `-m/--crop-margin` with explicit value)
- `-u, --cutout` parameter (functionality merged into noise removal workflow)
- `-I, --output-intermediate` parameter (redundant with `--output=png`)

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

[Unreleased]: https://github.com/hexin/icoft/compare/v0.2.1-dev...HEAD
[0.2.1-dev]: https://github.com/hexin/icoft/compare/v0.2.0...v0.2.1-dev
[0.2.0]: https://github.com/hexin/icoft/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hexin/icoft/releases/tag/v0.1.0
