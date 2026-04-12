"""Command-line interface for Icoft - Icon Forge.

Examples:
  # Basic usage - generate icons from original image
  icoft logo.png icons/

  # With processing steps
  icoft -m 10% -t logo.png icons/
  icoft -m 10% -B 15 logo.png icons/

  # Single file output
  icoft -s logo.png output.svg -o svg
  icoft -m 10% logo.png output.png -o png
"""

from importlib.metadata import version

import click
from rich.console import Console

console = Console()

# Get version from package metadata
__version__ = version("icoft")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_dir", type=click.Path(), required=False)
@click.option(
    "-m",
    "--crop-margin",
    "crop_margin",
    type=str,
    default=None,
    help="Margin for cropping (e.g., 5%, 10px)",
)
@click.option(
    "-t",
    "--transparent",
    "do_transparent",
    is_flag=True,
    default=False,
    help="Make background transparent",
)
@click.option(
    "-B",
    "--bg-threshold",
    "bg_threshold",
    type=int,
    default=10,
    help="Background removal tolerance (0-255, default: 10)",
)
@click.option(
    "-s",
    "--svg",
    "do_svg",
    is_flag=True,
    default=False,
    help="Enable vectorization (PNG to SVG)",
)
@click.option(
    "-S",
    "--svg-speckle",
    "svg_speckle",
    type=int,
    default=10,
    help="Filter SVG noise (1-100, default: 10)",
)
@click.option(
    "-P",
    "--svg-precision",
    "svg_precision",
    type=int,
    default=6,
    help="SVG color precision (1-16, default: 6)",
)
@click.option(
    "-o",
    "--output",
    "output_format",
    type=click.Choice(["png", "svg", "icon"]),
    default="icon",
    help="Output format (default: icon)",
)
@click.option(
    "-p",
    "--platforms",
    type=str,
    default="all",
    help="Comma-separated list of platforms (default: all)",
)
@click.option("-V", "--version", "show_version", is_flag=True, help="Show version and exit")
def main(
    input_file: str | None,
    output_dir: str | None,
    crop_margin: str | None,
    do_transparent: bool,
    bg_threshold: int,
    do_svg: bool,
    svg_speckle: int,
    svg_precision: int,
    output_format: str,
    platforms: str,
    show_version: bool,
) -> None:
    """Icoft - From Single Image to Full-Platform App Icons."""

    # Handle --version flag
    if show_version:
        console.print(f"[bold blue]icoft[/bold blue] [dim]v{__version__}[/dim]")
        return

    # Validate required arguments with clear error messages
    if input_file is None and output_dir is None:
        console.print("[red]Error:[/] Missing required arguments")
        console.print("  [bold]INPUT_FILE[/bold] and [bold]OUTPUT_DIR[/bold] are required.")
        console.print("\n[bold blue]Examples:[/]")
        console.print("  icoft logo.png icons/              # Generate icons from original")
        console.print("  icoft -m 10% logo.png icons/       # Crop + generate icons")
        console.print("  icoft -s logo.png out.svg -o svg   # Vectorize to SVG")
        console.print("\nUse [bold]-h[/bold] or [bold]--help[/bold] for more options.")
        raise SystemExit(1)

    if input_file is None:
        console.print("[red]Error:[/] Missing [bold]INPUT_FILE[/bold] argument")
        console.print("  Please specify the input image file.")
        console.print("\n[bold blue]Example:[/] icoft logo.png icons/")
        raise SystemExit(1)

    if output_dir is None:
        console.print("[red]Error:[/] Missing [bold]OUTPUT_DIR[/bold] argument")
        console.print("  Please specify the output directory or file path.")
        console.print("\n[bold blue]Examples:[/]")
        console.print("  icoft logo.png [bold]icons/[/bold]           # Output to directory")
        console.print("  icoft logo.png [bold]out.svg[/bold] -o svg   # Output to single file")
        raise SystemExit(1)

    from pathlib import Path

    input_path = Path(input_file)
    output_path = Path(output_dir)

    # Smart 判断：是单文件输出还是目录输出？
    # 规则：
    # 1. 如果 output 以 / 结尾 → 目录
    # 2. 如果 output 有图片扩展名 (.png, .jpg, .svg) → 文件
    # 3. 否则 → 目录
    is_single_file = output_dir.endswith("/") is False and output_path.suffix.lower() in [
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".ico",
        ".icns",
    ]

    # 创建输出目录（单文件输出时创建父目录）
    if is_single_file:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path.mkdir(parents=True, exist_ok=True)

    console.print("[bold blue]Icoft - Icon Forge[/bold blue]")
    console.print(f"Processing: {input_path}")
    console.print(f"Output: {output_path} ({'single file' if is_single_file else 'directory'})\n")

    # Check if any step flag was explicitly provided
    any_step_flagged = any(
        [
            crop_margin is not None,
            do_transparent,
            bg_threshold != 10,
            do_svg,
            svg_speckle != 10,
            svg_precision != 6,
        ]
    )

    # Determine which steps to execute
    if not any_step_flagged:
        # No flags - default: NO processing, only generate icons from original image
        crop_margin = None
        crop_enabled = False
        transparent_enabled = False
        do_svg = False
    else:
        # Enable steps based on which parameters were provided
        # -t or -B → transparent_enabled (simple background removal)
        transparent_enabled = do_transparent or bg_threshold != 10

        # Auto-enable steps based on parameter flags
        crop_enabled = crop_margin is not None
        do_svg = do_svg or (svg_speckle != 10 or svg_precision != 6)

    # --output=svg should auto-enable vectorization
    if output_format == "svg" and not do_svg:
        do_svg = True
        # Also enable transparent background if no other processing specified
        if not transparent_enabled:
            transparent_enabled = True

    # Priority 4: Determine output format
    # --output=icon (default) → generate icons
    # --output=png → save last processing step as PNG
    # --output=svg → save last processing step as SVG
    icon_enabled = output_format == "icon"

    try:
        from icoft.core.processor import ImageProcessor

        processor = ImageProcessor(input_path)
        step_num = 1

        # Determine the last step to save the final output
        # When --output=icon, always generate icons regardless of processing steps
        if icon_enabled:
            last_step = "icon"
        elif output_format == "svg":
            last_step = "svg"
        elif output_format == "png":
            if do_svg:
                last_step = "svg"
            elif transparent_enabled:
                last_step = "transparent"
            elif crop_enabled:
                last_step = "crop"
            else:
                last_step = "original"
        else:
            last_step = "icon"

        # Step 1: Crop borders
        if crop_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Cropping borders...")
            processor.crop_borders(margin=crop_margin)
            console.print("[green]✓[/green] Borders cropped")
            step_num += 1

            if last_step == "crop":
                last_output_path = output_path if is_single_file else output_path / "01_cropped.png"
                processor.save(last_output_path)
                console.print(
                    f"\n[bold green]Success![/] Cropped image saved to: {last_output_path}"
                )
                return

        # Step 2: Background processing (choose one method)
        # -t/-B: Simple background removal (detect corner color)
        # -T: Advanced watermark/noise removal (edge detection + adaptive threshold)
        if transparent_enabled:
            # Simple background removal
            console.print(f"[yellow]Step {step_num}:[/] Making background transparent...")
            processor.make_background_transparent(tolerance=bg_threshold)
            console.print("[green]✓[/green] Background made transparent")

            if last_step == "transparent":
                last_output_path = (
                    output_path if is_single_file else output_path / "02_transparent.png"
                )
                processor.save(last_output_path)
                console.print(
                    f"\n[bold green]Success![/] Transparent PNG saved to: {last_output_path}"
                )
                return
            step_num += 1

        # Step 4: Vectorization (optional)
        if do_svg:
            console.print(f"[yellow]Step {step_num}:[/] Vectorizing (PNG to SVG)...")
            try:
                import vtracer

                img = processor.image.convert("RGBA")
                pixels = list(img.getdata())

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

                if is_single_file:
                    last_output_path = output_path
                else:
                    last_output_path = output_path / "04_vectorized.svg"
                last_output_path.parent.mkdir(parents=True, exist_ok=True)
                last_output_path.write_text(svg_result, encoding="utf-8")
                console.print("[green]✓[/green] Vectorization complete")
                console.print(f"[dim]✓[/dim] Saved: {last_output_path.name}")

                # Save final output if this is the last step
                if last_step == "svg":
                    if output_format == "png":
                        # Save SVG result as PNG (rasterize)
                        # For now, just save the PNG before vectorization
                        last_output_path = (
                            output_path if is_single_file else output_path / "04_vectorized.png"
                        )
                        processor.save(last_output_path)
                        console.print(f"\n[bold green]Success![/] PNG saved to: {last_output_path}")
                    else:
                        console.print(f"\n[bold green]Success![/] SVG saved to: {last_output_path}")
                    return

            except ImportError:
                console.print("[red]Error:[/] Vectorization requires 'vtracer' package")
                console.print("[dim]Install with: pip install vtracer[/dim]")
                return

        # Step 5: Generate icons (default) or save PNG
        if icon_enabled:
            from icoft.core.generator import IconGenerator

            generator = IconGenerator(processor.image, output_path)

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

        elif output_format == "png" and last_step == "original":
            # --output=png with no processing steps: save original as PNG
            last_output_path = output_path if is_single_file else output_path / "original.png"
            processor.save(last_output_path)
            console.print(f"\n[bold green]Success![/] Original image saved to: {last_output_path}")

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        raise


if __name__ == "__main__":
    main()
