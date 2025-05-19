from rich.console import Console
from rich_pyfiglet import RichFiglet

console = Console()

rich_fig = RichFiglet(
    "Rich - PyFiglet",
    font="pagga_lite",
    colors=["#ff0000", "magenta1"],
    # horizontal=True,
    animation="gradient_down",
    border="ROUNDED",
    border_color="magenta1",
    # quality=15,
    fps=5,
    # dev_mode=True,
)

console.print(rich_fig)

# IMPORTANT NOTES:
# Why is there a border argument in the RichFiglet constructor?
# -----------------------------------------------------------------------------
# There are several reasons that placing a border on the RichFiglet after
# creating it will cause problems.
# 1. The RichFiglet cannot account for the border size when rendering.
#   This will create a problem where if the RichFiglet's width happens to be e
#   close to the width of the terminal (using up almost all of its available space),
#   the border will destroy the render and make it look jumbled.
#   By adding the border into the constructor, the RichFiglet can account for the
#   extra space needed by the border and padding when it calculates the available
#   space it has to render.
# 2. You cannot add a border onto a Live object after it has been created.
#   The Live object needs to be the top-level renderable. If you try to add a border
#   after the Live object has been created, it will not work and will usually
#   crash the program.
#   If you want a border while animating, the panel object has to go inside
#   the Live object. That is why the RichFiglet provides a border argument in
#   the constructor. It will include the border itself as part of its animation.

# panel = Panel(          # <-- This will cause issues and is not recommended.
#     rich_fig,
#     padding=(1, 4),
# )
# console.print(panel)
