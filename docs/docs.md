# Rich-PyFiglet<br>Documentation and Guide

## Installation

```sh
pip install rich-pyfiglet
```

Or using uv:

```sh
uv add rich-pyfiglet
```

## CLI mode

You can instantly try out Rich-PyFiglet with the included CLI using uv:

```sh
uvx rich-pyfiglet "Rich is awesome" --colors green3:purple -a gradient_down
```

or using pipx:

```sh
pipx run rich-pyfiglet "Rich is awesome" --colors blue1:magenta3 -h
```

## Getting Started

Import into your project with:

```py
from rich_pyfiglet import RichFiglet
```

Example of very basic usage:

```py
from rich.console import Console
from rich_pyfiglet import RichFiglet
console = Console()

rich_fig = RichFiglet(
    "Your Text Here",
    font="ansi_shadow",
    colors=["#ff0000", "bright_blue"],
)
console.print(rich_fig)
```

## Passing in multiple colors and set direction to horizontal

```py
rich_fig = RichFiglet(
    "Rich - PyFiglet",
    font="ansi_shadow",
    colors=["#ff0000", "bright_blue", "yellow", "green3"],
    horizontal=True,
)
console.print(rich_fig)
```

## Using animations

The 4 types of animations are:

- `gradient_up`: The Color gradient will flow vertically across the banner upwards.
- `gradient_down`: The Color gradient will flow vertically across the banner downwards.
- `smooth_strobe`: The entire banner will smoothly transition between colors
- `fast_strobe`: The entire banner will hard switch to the next color.

If you pass in multiple colors, they will all be used in the animation. The animation will cycle through all colors you passed in and then loop.

```py
rich_fig = RichFiglet(
    "Rich - PyFiglet",
    font="slant",
    colors=["#ff0000", "bright_blue", "yellow", "green3"],
    animation="smooth_strobe",
)
console.print(rich_fig)
```

## Advanced tweaking

For more fine-grained control, you can adjust the gradient quality and the animation FPS. FPS can be a float.

```py
rich_fig = RichFiglet(
    "Rich - PyFiglet",
    font="rounded",
    colors=["#ff0000", "bright_blue", "yellow", "green3"],
    animation="smooth_strobe",
    quality=10,
    fps=1.8,
)
console.print(rich_fig)
```

## Included border arguments

The RichFiglet takes arguments for border settings. This is completely necessary in order to ensure that it renders properly inside of borders. You might wonder, why not simply take the rendered figlet and put it inside a Rich Panel object after its been rendered? Well, this is prone to some problems.

The first is that the RichFiglet gets the terminal width and calculates how much space it has to render. Adding a border and padding after that throws off the calculation, and can mess up the render if your terminal just happens to be at the right size. The second issue is that the animations cannot be placed inside of a Panel object to place a border around them. It will cause the animation to stop working.

The RichFiglet solves both of these problems by rendering a border itself. Pass in your desired border settings as arguments in the constructor, and the RichFiglet will properly account for the space taken up by the border and padding to ensure it always renders properly in the available space as well as add a border around any animations you choose.

```py
rich_fig = RichFiglet(
    "Rich - PyFiglet",
    font="rounded",
    colors=["#ff0000", "magenta1"],
    border="ROUNDED",
    border_color="ff0000",
    border_padding = (1, 2),
)
console.print(rich_fig)
```

## Full example

Here is an example of a short script demonstrating almost all argument in the constructor:

```py
from rich.console import Console
from rich_pyfiglet import RichFiglet
console = Console()

rich_fig = RichFiglet(
    "Your Banner Here",
    font = "modular",
    width = 80,   # Bypass the auto-detection and set size manually
    colors = ["#ff0000", "magenta1", "blue3"],
    horizontal = True   # This will be ignored because animation is set
    animation = "fast_strobe",
    fps = 0.5,
    remove_blank_lines = True,
    border = "ROUNDED",
    border_padding = (1, 2),
    border_color = "#ff0000",
    dev_mode = True,
):
console.print(rich_fig)
console.print("The rest of your Rich script")
```

## API Reference

You can find the full API reference on the [reference page](reference.md).
