"""Command-line interface for Icoft - Icon Forge."""

import click
from rich.console import Console

console = Console()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_dir", type=click.Path(), required=False)
@click.option(
    "--preset",
    type=click.Choice(["minimal", "standard", "full", "icon"]),
    default=None,
    help="Quick preset configuration",
)
@click.option(
    "-c",
    "--crop",
    "do_crop",
    is_flag=True,
    default=None,
    help="Crop borders (default: enabled)",
)
@click.option(
    "-m",
    "--crop-margin",
    "crop_margin",
    type=str,
    default="5%",
    help="Margin for cropping (default: 5%)",
)
@click.option(
    "-u",
    "--cutout",
    "do_cutout",
    is_flag=True,
    default=None,
    help="Smart cutout to extract subject",
)
@click.option(
    "-T",
    "--cutout-threshold",
    "cutout_threshold",
    type=int,
    default=30,
    help="Smart cutout sensitivity (0-255, default: 30)",
)
@click.option(
    "-t",
    "--transparent",
    "do_transparent",
    is_flag=True,
    default=None,
    help="Make background transparent (default: enabled)",
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
    help="Filter small noise in SVG (default: 10)",
)
@click.option(
    "-P",
    "--svg-precision",
    "svg_precision",
    type=int,
    default=6,
    help="Color precision for SVG (default: 6)",
)
@click.option(
    "-i",
    "--icon",
    "do_icon",
    is_flag=True,
    default=None,
    help="Generate platform icons (default)",
)
@click.option(
    "-p",
    "--platforms",
    type=str,
    default="all",
    help="Comma-separated list of platforms (default: all)",
)
@click.option(
    "-I",
    "--output-intermediate",
    "output_intermediate",
    is_flag=True,
    help="Save intermediate processing steps",
)
@click.version_option(version="0.2.0-dev", prog_name="icoft")
def main(
    input_file: str | None,
    output_dir: str | None,
    preset: str | None,
    do_crop: bool | None,
    crop_margin: str,
    do_cutout: bool | None,
    cutout_threshold: int,
    do_transparent: bool | None,
    bg_threshold: int,
    do_svg: bool,
    svg_speckle: int,
    svg_precision: int,
    do_icon: bool | None,
    platforms: str,
    output_intermediate: bool,
) -> None:
    """
    Icoft - From AI Logo to Full-Platform App Icons.

    \b
    Processing Steps (can be combined):
      -c, --crop              Crop borders
      -u, --cutout            Smart cutout
      -t, --transparent       Make background transparent
      -s, --svg               Vectorize to SVG
      -i, --icon              Generate icons (default)

    \b
    Parameter Options:
      -m, --crop-margin=5%    Margin for cropping
      -T, --cutout-threshold  Cutout sensitivity
      -B, --bg-threshold      Background threshold
      -S, --svg-speckle       Filter SVG noise
      -P, --svg-precision     SVG color precision

    \b
    Presets:
      --preset=minimal        Only crop
      --preset=standard       Crop + cutout + transparent
      --preset=full           All steps + vectorization
      --preset=icon           Generate icons (default)

    \b
    Examples:
      # Quick start (default)
      icoft logo.png icons/

      # Combined short options (Unix-style: options first)
      icoft -cuts logo.png out/    # Process to SVG
      icoft -cuti logo.png out/    # Process to icons

      # Custom parameters
      icoft -cu -m 10% -T 40 -B 15 logo.png out/

      # Specific step output
      icoft -c logo.png out/       # Just crop
      icoft -cu logo.png out/      # Crop + cutout
      icoft -cut logo.png out/     # Crop + cutout + transparent
      icoft -s logo.png out/       # Just vectorize
    """
    # Show help if no arguments provided
    if input_file is None or output_dir is None:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    from pathlib import Path

    input_path = Path(input_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    console.print("[bold blue]Icoft - Icon Forge[/bold blue]")
    console.print(f"Processing: {input_path}")
    console.print(f"Output: {output_path}\n")

    # Determine which steps to execute
    use_preset = preset is not None

    # Priority 1: Preset configuration
    if use_preset:
        if preset == "minimal":
            crop_enabled = True
            cutout_enabled = False
            transparent_enabled = False
            icon_enabled = False
            do_svg = False
        elif preset == "standard":
            crop_enabled = True
            cutout_enabled = True
            transparent_enabled = True
            icon_enabled = True
            do_svg = False
        elif preset == "full":
            crop_enabled = True
            cutout_enabled = True
            transparent_enabled = True
            icon_enabled = False
            do_svg = True
        else:  # icon preset
            crop_enabled = True
            cutout_enabled = True
            transparent_enabled = True
            icon_enabled = True
            do_svg = False

    # Priority 3: Explicit step flags or smart defaults
    else:
        # Check if any step flag was explicitly provided
        any_step_flagged = any(
            [
                do_crop is not None,
                do_cutout is not None,
                do_transparent is not None,
                do_svg,
                do_icon is not None,
            ]
        )

        if not any_step_flagged:
            # No flags - default: full workflow with icon output
            crop_enabled = True
            cutout_enabled = True
            transparent_enabled = True
            do_svg = False
            icon_enabled = True
        else:
            # Some flags provided - only enable explicitly requested steps
            # Output is determined by the last step:
            # - If -i is specified: generate icons
            # - If -s is specified (and no -i): output SVG
            # - Otherwise: output the result of the last preprocessing step
            crop_enabled = do_crop if do_crop is not None else False
            cutout_enabled = do_cutout if do_cutout is not None else False
            transparent_enabled = do_transparent if do_transparent is not None else False
            do_svg = do_svg

            # Icon generation is only enabled if explicitly requested with -i
            icon_enabled = do_icon if do_icon is not None else False

        # Priority 4: Auto-enable steps based on parameter flags
        # If user specifies a non-default parameter, enable that step
        if crop_margin != "5%":
            crop_enabled = True
        if cutout_threshold != 30:
            cutout_enabled = True
        if bg_threshold != 10:
            transparent_enabled = True
        if svg_speckle != 10 or svg_precision != 6:
            do_svg = True

    try:
        from icoft.core.processor import ImageProcessor

        processor = ImageProcessor(input_path)
        step_num = 1

        # Determine the last step to save the final output
        if icon_enabled:
            last_step = "icon"
        elif do_svg:
            last_step = "svg"
        elif transparent_enabled:
            last_step = "transparent"
        elif cutout_enabled:
            last_step = "cutout"
        elif crop_enabled:
            last_step = "crop"
        else:
            last_step = "icon"  # Default to icon generation

        # Step 1: Crop borders
        if crop_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Cropping borders...")
            processor.crop_borders(margin=crop_margin)
            console.print("[green]✓[/green] Borders cropped")
            step_num += 1

            if output_intermediate:
                last_output_path = output_path / "intermediate" / "01_cropped.png"
                processor.save(last_output_path)
                console.print(f"[dim]✓[/dim] Saved: {last_output_path.name}")

            # Save final output if this is the last step
            if last_step == "crop":
                last_output_path = output_path / "01_cropped.png"
                processor.save(last_output_path)
                console.print(
                    f"\n[bold green]Success![/] Cropped image saved to: {last_output_path}"
                )
                return

        # Step 2: Smart cutout
        if cutout_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Applying smart cutout...")
            processor.smart_cutout(threshold=cutout_threshold)
            console.print("[green]✓[/green] Smart cutout applied")
            step_num += 1

            if output_intermediate:
                last_output_path = output_path / "intermediate" / "02_cutout.png"
                processor.save(last_output_path)
                console.print(f"[dim]✓[/dim] Saved: {last_output_path.name}")

            # Save final output if this is the last step
            if last_step == "cutout":
                last_output_path = output_path / "02_cutout.png"
                processor.save(last_output_path)
                console.print(
                    f"\n[bold green]Success![/] Cutout image saved to: {last_output_path}"
                )
                return

        # Step 3: Make background transparent
        if transparent_enabled:
            console.print(f"[yellow]Step {step_num}:[/] Converting background to transparent...")
            processor.make_background_transparent(tolerance=bg_threshold)
            console.print("[green]✓[/green] Background made transparent")
            step_num += 1

            if output_intermediate:
                last_output_path = output_path / "intermediate" / "03_transparent.png"
                processor.save(last_output_path)
                console.print(f"[dim]✓[/dim] Saved: {last_output_path.name}")

            # Save final output if this is the last step
            if last_step == "transparent":
                last_output_path = output_path / "03_transparent.png"
                processor.save(last_output_path)
                console.print(
                    f"\n[bold green]Success![/] Transparent PNG saved to: {last_output_path}"
                )
                return

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

                last_output_path = output_path / "04_vectorized.svg"
                last_output_path.parent.mkdir(parents=True, exist_ok=True)
                last_output_path.write_text(svg_result, encoding="utf-8")
                console.print("[green]✓[/green] Vectorization complete")
                console.print(f"[dim]✓[/dim] Saved: {last_output_path.name}")

                # Save final output if this is the last step
                if last_step == "svg":
                    console.print(f"\n[bold green]Success![/] SVG saved to: {last_output_path}")
                    return

            except ImportError:
                console.print("[red]Error:[/] Vectorization requires 'vtracer' package")
                console.print("[dim]Install with: pip install vtracer[/dim]")
                return

        # Step 5: Generate icons (default)
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

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        raise


if __name__ == "__main__":
    main()
