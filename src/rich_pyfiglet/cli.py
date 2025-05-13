from __future__ import annotations
from typing import get_args, cast
import click
from rich_pyfiglet.pyfiglet.fonts import ALL_FONTS
from rich_pyfiglet.rich_figlet import GRADIENT_DIRECTIONS


font_help = "Specify the font to use. Use 'list' to see available fonts."
colors_help = (
    "Pass in a color or a list of colors. Colors can be hex, RGB, or named colors. "
    "If using a list, separate colors with colons: 'red:green:blue' "
)
animate_help = "Animate the text. Requires at least 2 colors to be set."
quality_help = (
    "Set the gradient quality. Default is auto, which will calculate all gradients in "
    "your color list to match either the width (in horizontal mode) or the height "
    "(in vertical mode) of the rendered banner."
)
speed_help = "Set the animation speed (in seconds). Default is 0.1 seconds."
dir_help = (
    "Set the gradient direction. Can be 'vertical', 'horizontal', or 'none'. Default is vertical. "
    "'none' can be used in combination with animate to make a strobe effect."
)
dev_help = "Run CLI in verbose/dev mode. This will print extra debug information."


@click.command(context_settings={"ignore_unknown_options": False})
@click.argument("text", type=str, default=None, required=False)
@click.option("--list", "-l", is_flag=True, default=False, help="List available fonts.")
@click.option("--font", "-f", type=str, default=None, help=font_help)
@click.option("--colors", type=str, default=None, help=colors_help)
@click.option("--gradient_dir", "-dir", type=str, default="vertical", help=dir_help)
@click.option("--quality", "-q", type=int, default=None, help=quality_help)
@click.option("--animate", "-a", is_flag=True, default=False, help=animate_help)
@click.option("--speed", "-s", type=float, default=0.1, help=speed_help)
@click.option("--dev", "-v", is_flag=True, default=False, help=dev_help)
def cli(
    text: str | None,
    font: str | None,
    colors: str | None,
    animate: bool,
    quality: int | None,
    speed: float,
    gradient_dir: str,
    list: bool,
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
            click.echo("Use -l or --list to see available fonts.")

    # Providing a main argument will run the RichFiglet class in CLI mode.
    else:
        from rich_pyfiglet.rich_figlet import RichFiglet
        from rich.console import Console

        console = Console()

        if not isinstance(text, str):  # type: ignore (This is not unnecessary)
            click.echo("Text must be a string.")
            return

        if font is None:
            font = "ansi_shadow"

        if font not in get_args(ALL_FONTS):
            click.echo(f"Font '{font}' not found. Use --list to see available fonts.")
            return

        if gradient_dir not in get_args(GRADIENT_DIRECTIONS):
            click.echo("Gradient direction must be either 'vertical' or 'horizontal'.")
            return

        if animate and (colors is None or ":" not in colors):
            click.echo("Animate requires --colors to be set. Use a list of colors separated by colons.")
            return

        if animate and speed <= 0:
            click.echo("Animate requires speed be greater than 0.")
            return

        if animate and gradient_dir == "horizontal":
            click.echo(
                "Animating horizontal gradients is unfortunately not supported. "
                "(I tried, but couldn't fix the glitchiness.)"
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
                gradient_dir=cast(GRADIENT_DIRECTIONS, gradient_dir),
                animate=animate,
                quality=quality,
                speed=speed,
                dev_mode=dev,
            )
        )


def main() -> None:
    """Entry point for the application."""
    cli()


if __name__ == "__main__":
    main()
