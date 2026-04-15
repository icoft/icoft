"""Command-line interface for Icoft - Icon Forge.

Examples:
  # Generate full icon set
  icoft source_file.png dest_dir/

  # Crop and generate icons
  icoft -m 10% source_file.png dest_dir/

  # Crop + background removal + icons
  icoft -m 10% -t source_file.png dest_dir/

  # Output single processed PNG
  icoft -m 10% source_file.png output.png -o png

  # Output single SVG (auto-vectorizes)
  icoft source_file.png output.svg -o svg
"""

from importlib.metadata import version

import click
from rich.console import Console

console = Console()

# Get version from package metadata
__version__ = version("icoft")


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("source_file", type=click.Path(exists=True), required=False)
@click.argument("dest_dir", type=click.Path(), required=False)
@click.option(
    "-a",
    "use_ai_bg",
    is_flag=True,
    default=False,
    help="Use AI for background removal (U²-Net)",
)
@click.option(
    "-b",
    "--bg-threshold",
    "bg_threshold",
    type=int,
    default=0,
    help="Enable simple color-based background removal with threshold (0-255, default: 10 when enabled)",
)
@click.option(
    "--bg-color",
    "bg_color",
    type=str,
    default=None,
    help='Background color for output (hex: "#RRGGBB" or "#RGB", rgb: "R,G,B", or name: red, gray, etc.)',
)
@click.option(
    "-c",
    "--crop-margin",
    "crop_margin",
    type=str,
    default=None,
    help="Margin for cropping (e.g., 5%, 10px)",
)
@click.option(
    "-o",
    "--output",
    "output_format",
    type=click.Choice(["png", "svg", "icon"]),
    default="icon",
    help="Output format: icon (directory), png (single file), svg (single file)",
)
@click.option(
    "-p",
    "--platforms",
    type=str,
    default="all",
    help="Comma-separated platforms: windows, macos, linux, web (default: all)",
)
@click.option(
    "-s",
    "--svg",
    "svg_mode",
    type=click.Choice(["normal", "embed"]),
    default=None,
    help="Enable SVG output: normal (true vector, scalable) or embed (PNG in SVG wrapper, NOT scalable, preserves gradients/photos)",
)
@click.option(
    "-S",
    "--svg-speckle",
    "svg_speckle",
    type=int,
    default=10,
    help="Filter SVG noise (1-100, default: 10, only for 'normal' mode)",
)
@click.option(
    "-P",
    "--svg-precision",
    "svg_precision",
    type=int,
    default=6,
    help="SVG color precision (1-16, default: 6, only for normal mode)",
)
@click.option("-V", "--version", "show_version", is_flag=True, help="Show version and exit")
def main(
    source_file: str | None,
    dest_dir: str | None,
    use_ai_bg: bool,
    bg_threshold: int,
    bg_color: str | None,
    crop_margin: str | None,
    output_format: str,
    platforms: str,
    svg_mode: str | None,
    svg_speckle: int,
    svg_precision: int,
    show_version: bool,
) -> None:
    """Icoft - From Single Image to Full-Platform App Icons."""

    # Handle --version flag
    if show_version:
        console.print(f"Icoft version {__version__}")
        return

    # Validate arguments
    if source_file is None:
        console.print("[red]Error:[/] Missing source file argument")
        console.print("\nUsage: icoft [OPTIONS] SOURCE_FILE DEST_DIR")
        console.print("       icoft [OPTIONS] SOURCE_FILE OUTPUT_FILE -o FORMAT")
        console.print("\nUse -h or --help for more information.")
        raise SystemExit(1)

    if dest_dir is None:
        console.print("[red]Error:[/] Missing destination directory or output file argument")
        console.print("\nUsage: icoft [OPTIONS] SOURCE_FILE DEST_DIR")
        console.print("       icoft [OPTIONS] SOURCE_FILE OUTPUT_FILE -o FORMAT")
        console.print("\nUse -h or --help for more information.")
        raise SystemExit(1)

    try:
        from pathlib import Path

        from icoft.core.processor import ImageProcessor

        source_path = Path(source_file)
        output_path = Path(dest_dir)

        # Get base filename for outputs
        base_filename = source_path.stem

        # Determine if we're outputting to a single file or directory
        if output_format in ["png", "svg"]:
            # When -o png/svg is specified, check if output_path is a directory
            # If so, generate filename automatically
            if output_path.is_dir() or not output_path.suffix:
                is_single_file = False
                output_path = output_path / f"{base_filename}.{output_format}"
            else:
                is_single_file = True
        else:
            is_single_file = output_path.suffix in [".png", ".svg"]

        console.print("[bold cyan]Icoft - Icon Forge[/bold cyan]")
        console.print(f"Processing: {source_path}")
        if is_single_file:
            console.print(f"Output: {output_path} (single file)\n")
        else:
            console.print(f"Output: {output_path} (directory)\n")

        # Initialize processor
        processor = ImageProcessor(source_path)

        # Track step number for display
        step_num = 1

        # Determine which processing steps are enabled
        crop_enabled = crop_margin is not None
        transparent_enabled = use_ai_bg or bg_threshold != 0
        icon_enabled = output_format == "icon" and not is_single_file

        # Step 1: Cropping (optional)
        if crop_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Cropping borders...")
            processor.crop_borders(crop_margin)
            console.print("[green]✓[/green] Borders cropped")
            step_num += 1

            # Continue to final output step

        # Step 2: Background processing
        # -B: Simple color-based method
        # -A: AI-based method (U²-Net)
        # -A -B: AI + refinement
        if transparent_enabled:
            if use_ai_bg:
                # AI-based background removal
                # Phase 1: Extract background color BEFORE AI (for optional refinement)
                extracted_bg_color = None
                if bg_threshold != 0:  # -B specified with AI for refinement
                    console.print(f"[yellow]Step {step_num}:[/] Extracting background color...")
                    extracted_bg_color = processor.extract_background_color()
                    if extracted_bg_color is not None:
                        console.print(
                            f"[green]✓[/green] Background color extracted: {extracted_bg_color.astype(int)}"
                        )
                    else:
                        console.print(
                            "[yellow]⚠[/yellow] No background color detected, skipping refinement"
                        )
                    step_num += 1

                # Phase 2: AI-based background removal
                console.print(f"[yellow]Step {step_num}:[/] Removing background with AI...")
                try:
                    processor.remove_background_ai(bg_threshold=bg_threshold)
                    console.print("[green]✓[/green] Background removed using AI (U²-Net)")
                except ImportError as e:
                    console.print(f"[red]Error:[/] {e}")
                    console.print("[yellow]Tip:[/] Install with: uv sync --extra ai")
                    raise SystemExit(1) from None
                step_num += 1

                # Phase 3: Optional color-based refinement AFTER AI
                if extracted_bg_color is not None:
                    console.print(
                        f"[yellow]Step {step_num}:[/] Applying color-based refinement (threshold={bg_threshold})..."
                    )
                    processor.refine_transparency(
                        bg_color=extracted_bg_color, tolerance=bg_threshold
                    )
                    console.print(
                        "[green]✓[/green] Color-based refinement applied (handles both opaque and semi-transparent pixels)"
                    )
                    step_num += 1
            else:
                # Simple color-based background removal (-B flag)
                threshold = bg_threshold if bg_threshold != 0 else 10  # Default to 10 if just -B
                console.print(f"[yellow]Step {step_num}:[/] Making background transparent...")
                processor.make_background_transparent(tolerance=threshold)
                console.print(
                    f"[green]✓[/green] Background made transparent (color-based, threshold={threshold})"
                )
                step_num += 1

            # Apply background color if specified
            if bg_color is not None:
                console.print(f"[yellow]Step {step_num}:[/] Applying background color...")
                try:
                    processor.apply_background(bg_color)
                    console.print(f"[green]✓[/green] Background color applied: {bg_color}")
                except ValueError as e:
                    console.print(f"[red]Error:[/] Invalid color format: {e}")
                    return
                step_num += 1

            # Continue to final output step

        # Apply background color for SVG/icon output (if not already applied in transparent step)
        if bg_color is not None and not transparent_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Applying background color...")
            try:
                processor.apply_background(bg_color)
                console.print(f"[green]✓[/green] Background color applied: {bg_color}")
            except ValueError as e:
                console.print(f"[red]Error:[/] Invalid color format: {e}")
                return
            step_num += 1

        # Step 4: SVG generation (only when -o svg)
        svg_content_for_generator = None
        if output_format == "svg":
            # Default to normal mode if -s is not specified
            if svg_mode is None:
                svg_mode = "normal"
            if svg_mode == "embed":
                # Embed PNG as base64 into SVG (preserves gradients perfectly)
                console.print(f"[yellow]Step {step_num}:[/] Generating SVG (embedded PNG)...")
                import base64
                import io

                img = processor.image.convert("RGBA")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                png_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                svg_result = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img.width} {img.height}" width="{img.width}" height="{img.height}">
  <image href="data:image/png;base64,{png_base64}" width="{img.width}" height="{img.height}"/>
</svg>"""
            else:
                # Vector tracing with vtracer
                console.print(f"[yellow]Step {step_num}:[/] Vectorizing (PNG to SVG)...")
                try:
                    import re

                    import vtracer  # type: ignore[import-untyped]

                    img = processor.image.convert("RGBA")
                    pixels = list(img.getdata())  # type: ignore[arg-type]

                    svg_result = vtracer.convert_pixels_to_svg(
                        pixels,
                        img.size,
                        colormode="color",
                        hierarchical="stacked",
                        mode="spline",
                        filter_speckle=svg_speckle,
                        color_precision=svg_precision,
                        corner_threshold=60,
                        length_threshold=4.0,
                        splice_threshold=45,
                    )

                    # Fix viewBox: vtracer doesn't set it, causing display issues with transforms
                    # The paths start from (0,0) and are translated by transform attribute
                    # So viewBox should be from (0,0) with image dimensions
                    if "viewBox" not in svg_result:
                        # Add simple viewBox starting from origin
                        svg_result = re.sub(
                            r"<svg([^>]*)>",
                            f'<svg\\1 viewBox="0 0 {img.width} {img.height}">',
                            svg_result,
                            count=1,
                        )

                    # For normal mode, save the SVG content for high-quality icon generation
                    svg_content_for_generator = svg_result
                except ImportError:
                    console.print("[red]Error:[/] Vectorization requires 'vtracer' package")
                    console.print("[dim]Install with: pip install vtracer[/dim]")
                    return

            # output_path already contains the full filename from initialization
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_result, encoding="utf-8")
            console.print(f"[green]✓[/green] SVG generation complete (mode: {svg_mode})")
            console.print(f"[dim]✓[/dim] Saved: {output_path.name}")
            console.print(f"\n[bold green]Success![/] SVG saved to: {output_path}")
            return

        # Step 5: Generate icons (default) or save PNG
        if icon_enabled:
            from icoft.core.generator import IconGenerator

            generator = IconGenerator(
                processor.image, output_path, svg_content=svg_content_for_generator
            )

            platform_list = (
                platforms.split(",") if platforms != "all" else ["windows", "macos", "linux", "web"]
            )

            for platform in platform_list:
                platform = platform.strip().lower()
                if platform == "windows":
                    console.print("[yellow]Generating:[/] Windows icons...")
                    generator.generate_windows()
                    console.print("[green]✓[/green] Windows icons generated")
                elif platform == "macos":
                    console.print("[yellow]Generating:[/] macOS icons...")
                    generator.generate_macos()
                    console.print("[green]✓[/green] macOS icons generated")
                elif platform == "linux":
                    console.print("[yellow]Generating:[/] Linux icons...")
                    generator.generate_linux()
                    console.print("[green]✓[/green] Linux icons generated")
                elif platform == "web":
                    console.print("[yellow]Generating:[/] Web icons...")
                    generator.generate_web()
                    console.print("[green]✓[/green] Web icons generated")
                else:
                    console.print(f"[red]Warning:[/] Unknown platform: {platform}")

            console.print(f"\n[bold green]Success![/] All icons generated in: {output_path}")

        elif output_format == "png":
            # Save final PNG output (handles crop, transparent, original, and svg-rasterize steps)
            processor.save(output_path)
            console.print(f"\n[bold green]Success![/] PNG saved to: {output_path}")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise


if __name__ == "__main__":
    main()
