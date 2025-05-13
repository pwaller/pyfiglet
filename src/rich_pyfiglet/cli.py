from __future__ import annotations
from typing import get_args, cast
import click
from rich_pyfiglet.pyfiglet.fonts import ALL_FONTS
from rich_pyfiglet.rich_figlet import ANIMATION_TYPE


colors_help = (
    "Pass in a color or a list of colors. Colors can be hex, RGB, or named colors. "
    "If using a list, separate colors with colons: 'red:green:blue' "
)
animate_help = "Animate the text. Requires at least 2 colors to be set."
animation_help = (
    "Set the animation type. Can be 'gradient_up', 'gradient_down', 'smooth_strobe', or 'fast_strobe'. "
)
quality_help = (
    "Set the gradient quality. Default is auto, which will calculate all gradients in "
    "your color list to match either the width (in horizontal mode) or the height "
    "(in vertical mode) of the rendered banner."
)
fps_help = (
    "Set the animation frames per second. Default is 5 fps, unless using the "
    "'fast_strobe' animation type, which defaults to 1.5 fps."
)
dir_help = (
    "Flag to render the gradient horizontally. "
    "Note that this setting will be ignored if animate is set to True."
)
dev_help = "Run CLI in verbose/dev mode. This will print extra debug information."


@click.command(context_settings={"ignore_unknown_options": False})
@click.argument("text", type=str, default=None, required=False)
@click.option("--list", "-l", is_flag=True, default=False, help="List available fonts.")
@click.option("--font", "-f", type=str, default=None, help="Specify the font to use.")
@click.option("--colors", type=str, default=None, help=colors_help)
@click.option("--horizontal", "-h", is_flag=True, default=False, help=dir_help)
@click.option("--quality", "-q", type=int, default=None, help=quality_help)
@click.option("--animation", "-a", type=str, default=None, help=animation_help)
@click.option("--fps", type=float, default=None, help=fps_help)
@click.option("--dev", "-v", is_flag=True, default=False, help=dev_help)
def cli(
    text: str | None,
    list: bool,
    font: str | None,
    colors: str | None,
    horizontal: bool,
    quality: int | None,
    animation: str | None,
    fps: float | None,
    dev: bool = False,
) -> None:
    """CLI for Rich-PyFiglet"""

    # If no main argument is provided, check for the --list flag.
    if text is None:
        if list:
            click.echo("Available fonts:")
            for fontfoo in get_args(ALL_FONTS):
                click.echo(f"- {fontfoo}")
            return
        else:
            click.echo("Use --help for more information.")

    # Providing a main argument will run the RichFiglet class in CLI mode.
    else:
        from rich_pyfiglet.rich_figlet import RichFiglet
        from rich.console import Console

        console = Console()

        if font is None:
            font = "ansi_shadow"

        if font not in get_args(ALL_FONTS):
            click.echo(f"Font '{font}' not found. Use --list to see available fonts.")
            return

        if animation and (colors is None or ":" not in colors):
            click.echo("Animate requires --colors to be set. Use a list of colors separated by colons.")
            return

        if animation and fps and fps <= 0:
            click.echo("Animate requires fps be greater than 0.")
            return

        if animation and animation not in get_args(ANIMATION_TYPE):
            click.echo(
                "Animation type must be 'gradient_up', 'gradient_down', 'smooth_strobe', or 'fast_strobe'."
            )
            return

        if colors:
            colors_list = colors.split(":")
        else:
            colors_list = None

        console.print(
            RichFiglet(
                text,
                font=cast(ALL_FONTS, font),
                colors=colors_list,
                horizontal=horizontal,
                animation=cast(ANIMATION_TYPE, animation),
                quality=quality,
                fps=fps,
                dev_mode=dev,
            )
        )


def main() -> None:
    """Entry point for the application."""
    cli()


if __name__ == "__main__":
    main()
