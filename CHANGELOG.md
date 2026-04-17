# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-04-17

### Added
- **iOS platform support**: Complete iOS icon set generation with Asset Catalog
  - All required sizes for iPhone, iPad, and App Store (13 icons total)
  - Contents.json configuration file for Xcode integration
  - RGB mode icons (no alpha channel) as per iOS requirements
  - Support for notification, settings, Spotlight, and app icons
- **Android platform support**: Full adaptive icon generation
  - Adaptive icons with foreground/background separation (Android 8.0+)
  - Legacy icons for backward compatibility
  - All density buckets: mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi
  - Google Play Store icon (512x512)
  - Installation instructions and AndroidManifest snippet
- PWA manifest.json enhanced with `background_color` and `theme_color` fields
- Additional PWA manifest fields: `name`, `short_name`, `start_url`, `display`

### Changed
- Updated `apple-touch-icon.png` to RGB mode (removed alpha channel for iOS compatibility)
- CLI help text updated to include iOS and Android in platform options
- Default platform list now includes all 6 platforms: windows, macos, linux, web, ios, android

### Fixed
- Icon compliance issues across all platforms
- iOS touch icon transparency issue (now properly converted to RGB)
- PWA manifest.json missing required fields

## [0.5.2] - 2026-04-17

### Added
- Keywords to pyproject.toml for better PyPI search visibility

## [0.4.3] - 2026-04-15

### Added
- Enhanced CI/CD Pipeline documentation with complete GitHub Actions example
- Added Key Benefits and Popular Use Cases sections for CI/CD integration

### Changed
- Renamed optional dependency from `[icon]` to `[cairosvg]` for clarity
- Updated README image links to use GitHub raw URLs for PyPI display
- Improved installation instructions with complete commands for all package managers

### Fixed
- Fixed image display on PyPI by converting relative paths to absolute GitHub URLs

## [0.4.2] - 2026-04-15

### Added
- `--bg-color` option for adding background color to output (hex, RGB, or named colors)
- Support for color formats: `#RRGGBB`, `#RGB`, `R,G,B`, and named colors (red, gray, etc.)
- Background color applied to PNG, SVG, and icon generation outputs

### Changed
- CLI options reordered alphabetically for better organization
- SVG mode help text clarified: `embed` mode is NOT scalable
- README updated with SVG mode explanations

### Fixed
- Variable name conflict between `--bg-color` parameter and internal `bg_color` variable

## [0.4.1] - 2026-04-15

### Fixed
- Fix step numbering in CLI output when using `-a -b` together
- Fix `-o png` incorrectly generating SVG when `--svg` option was also specified
- `refine_transparency()` now handles semi-transparent pixels properly
- Remove redundant step number increment logic

### Changed
- SVG generation now only executes when `-o svg` is explicitly specified
- Improved background refinement to handle AI-generated edge artifacts

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
