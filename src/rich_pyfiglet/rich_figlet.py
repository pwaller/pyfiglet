"""Module for the RichPyFiglet class"""

# ~ Type Checking (Pyright and MyPy) - Strict Mode
# ~ Linting - Ruff
# ~ Formatting - Black - max 110 characters / line

from __future__ import annotations
from typing import get_args, Literal, Callable
import os
import time
import threading
from functools import partial
from queue import Queue, Empty

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.containers import Lines
from rich.style import Style
from rich.live import Live
from rich.measure import Measurement
from rich.color import Color, blend_rgb
from rich.panel import Panel

from rich_pyfiglet.pyfiglet import Figlet
from rich_pyfiglet.pyfiglet.fonts import ALL_FONTS
from rich_pyfiglet.box_constants import BOX_STYLES, BOXES

ANIMATION_TYPE = Literal["gradient_up", "gradient_down", "smooth_strobe", "fast_strobe"]


class RichFiglet:

    def __init__(
        self,
        text: str,
        font: ALL_FONTS = "standard",
        width: int | None = None,
        colors: list[str] | None = None,
        horizontal: bool = False,
        quality: int | None = None,
        animation: ANIMATION_TYPE | None = None,
        fps: float | None = None,
        remove_blank_lines: bool = False,
        border: BOX_STYLES | None = None,
        border_padding: tuple[int, int] = (1, 2),
        border_color: str | None = None,
        dev_mode: bool = False,
    ):
        """Create a RichFiglet object.

        Args:
            text: The text to render.
            font: The font to use. Defaults to 'standard'.
            width: The width of the rendered text. If None, will use the terminal width.
            colors: A list of colors to use for gradients or animations. Each color can be a name, hex code,
                or RGB triplet. If None, no gradient or animation will be applied. For available named colors,
                see: https://rich.readthedocs.io/en/stable/appendix/colors.html
            horizontal: Make the gradient render horizontally . This will be ignored if `animate` is True.
            quality: The number of steps to blend between two colors. Defaults to None, which enables
                auto mode. Auto mode sets the quality based on the width or height of the rendered banner.
                One exception: if `animate` is True and `animation_type` is 'smooth_strobe',
                auto mode will default to 10 steps per gradient.
            animation:
                - 'gradient_up': The Color gradient will flow vertically across the banner upwards.
                - 'gradient_down': The Color gradient will flow vertically across the banner downwards.
                - 'smooth_strobe': The entire banner will smoothly transition between colors
                - 'fast_strobe': The entire banner will hard switch to the next color.
                Recommended to lower the FPS to avoid giving people seizures.
            fps: Frames per second for the animation. This is a float so that you can set it to values
                such as 0.5 if you desire.
            remove_blank_lines: When True, all blank lines from the inside of the rendered ASCII art
                will be removed. Some fonts have gaps between the lines- this will remove them and
                compress the banner down to the minimum size.
            border: The box style to use for the border. Can be any of the box styles from Rich.
                Note that border is an argument because it is necessary for the RichFiglet to
                take the border and padding into account when rendering. It is recommended to use
                the border argument in the constructor, rather than adding a border afterwards.
            border_padding: The padding to use for the border. Defaults to (1, 2) which is (top/bottom, left/right).
            border_color: The color of the border. Can be a name, hex code, or RGB triplet.
            dev_mode: When True, will print debug information to the console.
        """

        #######################
        # ~ Validate Inputs ~ #
        #######################

        if not text:
            raise ValueError("Text cannot be empty. Please provide a valid text string.")
        if font not in get_args(ALL_FONTS):
            raise ValueError(f"Font {font} is not in the fonts folder.")
        if animation and (colors is None or len(colors) < 2):
            raise ValueError("At least two colors are required for animation.")
        if animation and fps and fps <= 0:
            raise ValueError("Frames per second must be greater than 0.")
        if quality and (colors is None or len(colors) < 2):
            raise ValueError("At least two colors are required to set a gradient quality.")
        if quality and quality < 2:
            raise ValueError("Gradient Quality must be 2 or higher.")
        if animation and animation not in ["gradient_up", "gradient_down", "smooth_strobe", "fast_strobe"]:
            raise ValueError(
                "Animation type must be 'gradient_up', 'gradient_down', 'smooth_strobe', or 'fast_strobe'."
            )

        terminal_width = None
        if width:
            # Pyright complains if I use 'if isinstance(width, int)' here.
            assert isinstance(width, int), "Width must be an integer."
            if width < 1:
                raise ValueError("Width must be greater than 0.")
        else:
            terminal_width = self.get_terminal_width()
            if terminal_width:
                width = (terminal_width - (border_padding[1] * 2) - 2) if border else terminal_width
                # terminal_width-(border_padding[1]*2)-2    This subtracts the left/right padding
                # and border from our available space in which we can render the text.

            else:
                width = 60  # Fallback width

        ###########################################

        self.text = text
        self.font = font
        self.colors = colors
        self.horizontal = horizontal
        self.animation = animation
        self.quality = quality
        self.border = border
        self.border_padding = border_padding
        self.border_color = border_color
        self.remove_blank_lines = remove_blank_lines
        self.animation_running = False
        self.dev_mode = dev_mode
        user_set_quality = False
        if quality:
            user_set_quality = True
        if animation:
            # Queue to store pre-rendered frames
            self.frame_queue: Queue[Lines | Panel] = Queue(maxsize=3)

        if animation == "fast_strobe":
            self.fps = fps if fps else 1.5  # default for fast strobe is lower
        else:
            self.fps = fps if fps else 5.0

        self.gradient: list[Color] = []
        parsed_colors: list[Color] = []

        #####################
        # ~ Parse Colors  ~ #
        #####################
        # This will raise an error if any of the colors are invalid.
        if colors:
            for color in colors:
                color_obj = self.parse_color(color)
                parsed_colors.append(color_obj)
            if self.dev_mode:
                for parsed_color in parsed_colors:
                    print(f"Color: {parsed_color}")

        self.border_style_obj: str | Style = "none"
        if border_color:
            self.border_style_obj = Style(color=self.parse_color(border_color))
            if self.dev_mode:
                print(f"Border color: {self.border_style_obj}")

        #####################
        # ~ Render Figlet ~ #
        #####################

        self.figlet = Figlet(font=font, width=width)
        self.render_str = self.figlet.renderText(text)
        rendered_strings_list = self.render_str.splitlines()

        # Remove leading and trailing blank lines LOOPER
        while True:
            lines_cleaned: list[str] = []
            for i, line in enumerate(rendered_strings_list):
                if remove_blank_lines:
                    if all(c == " " for c in line):  # if line is blank, skip it
                        pass
                    else:
                        lines_cleaned.append(line)  # Only append the lines we want to keep.
                else:
                    # If remove_blank_lines is False, we want to keep the inner blank lines,
                    # but remove any leading and trailing blank lines.
                    # if first line, and blank:
                    if i == 0 and all(c == " " for c in line):
                        pass
                    # elif last line, and blank:
                    elif i == len(rendered_strings_list) - 1 and all(c == " " for c in line):
                        pass
                    else:
                        lines_cleaned.append(line)

            if lines_cleaned == rendered_strings_list:  # if there's no changes,
                break  #                           then we can continue.
            else:
                rendered_strings_list = lines_cleaned
                # If lines_cleaned is different, that means there was
                # a change. So set render_lines to lines_cleaned and restart loop.

        # This is our finished final render (without color).
        # Convert it into a Lines object for Rich rendering:
        self.rendered_lines = Lines()
        for line in rendered_strings_list:
            self.rendered_lines.append(Text(line))

        # This is needed for __rich_measure__
        width_foo = len(max(rendered_strings_list, key=len))
        added_by_border = 2 if border else 0
        self.reported_width = width_foo + (self.border_padding[1] * 2) + added_by_border
        if self.dev_mode:
            print(f"Terminal width: {terminal_width}")
            print(f"Width: {self.reported_width}")
            print(f"Height: {len(rendered_strings_list)}")

        #####################################
        # ~ Color / Gradients / Animation ~ #
        #####################################

        if len(parsed_colors) == 0:
            # If there's no colors, we don't need to do anything else.
            return

        elif len(parsed_colors) == 1:
            for line in self.rendered_lines:
                line.stylize(Style(color=parsed_colors[0]))
            return

        elif len(parsed_colors) > 1:

            if not animation or animation in ["gradient_up", "gradient_down"]:

                num_of_gradients = len(parsed_colors) - 1  # 2 colors would mean 1 transition.
                if animation or not self.horizontal:
                    quality_float = quality if quality else len(rendered_strings_list) / num_of_gradients
                else:  # horizontal:
                    quality_float = (
                        quality if quality else len(max(rendered_strings_list, key=len)) / num_of_gradients
                    )

                if quality_float <= 1:
                    quality = 1
                    if self.dev_mode:
                        print(
                            f"ERROR: Quality is too low: {quality_float}. Setting to 1. This means "
                            "you have provided too many colors to fit inside your finished render. "
                            "Reduce the number of colors to see them all."
                        )
                else:
                    quality = int(quality_float)
                if self.dev_mode:
                    print(f"Gradient quality: {quality}")

                for i in range(len(parsed_colors) - 1):  # stop at second to last color because of [i + 1]
                    self.gradient += self.make_gradient(parsed_colors[i], parsed_colors[i + 1], quality)

                if self.dev_mode:
                    print(f"Colors in gradient before leftover: {len(self.gradient)}")

                if animation or not self.horizontal:
                    leftover = len(self.rendered_lines) - len(self.gradient)
                else:  # horizontal:
                    leftover = len(max(rendered_strings_list, key=len)) - len(self.gradient)

                if not user_set_quality:
                    if leftover > 0:
                        for _ in range(leftover):  # fill in the leftover lines with the last color
                            self.gradient.append(self.gradient[-1])
                    if self.dev_mode:
                        print(f"Colors in gradient after leftover: {len(self.gradient)}")

                # This will make the last color blend back into the first color.
                # This is normally not visible unless animating, or the user has set a
                # custom quality that is making the colors repeat.
                self.gradient += self.make_gradient(parsed_colors[-1], parsed_colors[0], quality)
                if self.dev_mode:
                    print(f"Colors in gradient after looping: {len(self.gradient)}")

                if animation or not self.horizontal:
                    self.rendered_with_colors = self._build_with_gradient("vertical")
                else:  # horizontal:
                    self.rendered_with_colors = self._build_with_gradient("horizontal")

            else:  # Animating and animation mode is smooth_strobe or fast_strobe

                if animation == "smooth_strobe":
                    quality = quality if quality else 10

                    for i in range(len(parsed_colors) - 1):  # stop at second to last color because of [i + 1]
                        self.gradient += self.make_gradient(parsed_colors[i], parsed_colors[i + 1], quality)

                    if self.dev_mode:
                        print(f"Colors in gradient: {len(self.gradient)}")

                    # Blend last color back into first color
                    self.gradient += self.make_gradient(parsed_colors[-1], parsed_colors[0], quality)
                    if self.dev_mode:
                        print(f"Colors in gradient after looping: {len(self.gradient)}")

                    # Set the first color for our strobe animation
                    for line in self.rendered_lines:
                        line.stylize(Style(color=self.gradient[0]))

                else:  # animation type is "fast_strobe"

                    self.gradient = parsed_colors

                    for line in self.rendered_lines:
                        line.stylize(Style(color=self.gradient[0]))
                    # In fast strobe mode, we don't require any built gradient, so just use
                    # the parsed colors as the gradient.

    #########################
    # ~ Utility Functions ~ #
    #########################

    def get_terminal_width(self) -> int | None:
        """Get the terminal size.

        Returns:
            The width of the terminal in characters, or None if it cannot be determined."""
        try:
            size = os.get_terminal_size()
            return size.columns
        except Exception:
            return None

    def parse_color(self, color: str) -> Color:
        """Parse a color string into a Color object.

        Args:
            color: The color string to parse. Can be a name, hex code, or RGB triplet.

        Returns:
            A Rich Color object representing the parsed color."""
        try:
            color2_obj = Color.parse(color)  # Check if the color is valid
        except Exception as e:
            raise e
        else:
            return color2_obj

    def make_gradient(self, color1: Color, color2: Color, steps: int) -> list[Color]:
        """
        Generate a smooth gradient between two colors.

        Args:
            color1: Starting color (can be name, hex, rgb)
            color2: Ending color (can be name, hex, rgb)
            steps: Number of colors in the gradient

        Returns:
            A list of Rich Color objects representing the gradient."""
        if steps <= 1:
            raise ValueError("Number of steps must be greater than 1.")

        triplet1 = color1.get_truecolor()
        triplet2 = color2.get_truecolor()

        gradient: list[Color] = []
        for i in range(steps):
            cross_fade = i / (steps - 1)
            # EXAMPLE if steps = 5:
            # i=0:       0 / (5 - 0) = 0.0
            # i=1:       1 / (5 - 1) = 0.25
            # i=2:       2 / (5 - 1) = 0.5
            # i=3:       3 / (5 - 1) = 0.75
            # i=4:       4 / (5 - 1) = 1.0
            blended_triplet = blend_rgb(triplet1, triplet2, cross_fade)
            blended_color = Color.from_triplet(blended_triplet)
            gradient.append(blended_color)

        return gradient
        # Explanation:
        # the function blend_rgb takes two RGB triplets and a cross-fade value (0 to 1)
        # the cross-fade value determines how much of each color to mix. You can think
        # of it as a percentage: 0.5 is a perfect 50/50 mix of the two colors.
        # 0.2 would be 20% of the first color and 80% of the second color, and so on.

        # So when we divide i by the amount of steps (minus 1), we get a series of values
        # starting at 0 and ending at 1. For example, if steps is 5, the values would be:
        # 0.0, 0.25, 0.5, 0.75, 1.0 (notice dividing by 4, to make 5 steps).

    ###########################
    # ~ Rendering Functions ~ #
    ###########################

    def _build_with_gradient(self, gradient_dir: str) -> Lines:

        rendered_with_colors = self.rendered_lines

        if gradient_dir == "vertical":

            for i, line in enumerate(rendered_with_colors):
                color_index = i % len(self.gradient)
                line.stylize(Style(color=self.gradient[color_index]))

        elif gradient_dir == "horizontal":

            for i, line in enumerate(rendered_with_colors):
                for j in range(len(line)):
                    # Same index positions across all lines get the same color
                    color_index = j % len(self.gradient)
                    # start at j, end at j + 1 - this is another way of saying "only color at j"
                    line.stylize(Style(color=self.gradient[color_index]), j, j + 1)

        else:
            raise ValueError("Invalid gradient direction. Must be 'vertical' or 'horizontal'.")

        return rendered_with_colors

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:

        if not self.animation:

            if self.gradient:
                if self.border:
                    panel = Panel(
                        self.rendered_with_colors,
                        box=BOXES[self.border],
                        padding=self.border_padding,
                        width=self.reported_width,
                        border_style=self.border_style_obj,
                    )
                    yield panel
                else:
                    yield self.rendered_with_colors

            # If there's no gradient, it's either plain or 1 color
            else:
                if self.border:
                    panel = Panel(
                        self.rendered_lines,
                        box=BOXES[self.border],
                        padding=self.border_padding,
                        width=self.reported_width,
                        border_style=self.border_style_obj,
                    )
                    yield panel
                else:
                    yield self.rendered_lines

        else:  # animate is True:

            if self.animation in ["gradient_up", "gradient_down"]:
                self._vertical_animation(console, self.rendered_with_colors, self.gradient, self.fps)
            elif self.animation == "smooth_strobe":
                self._smooth_strobe_animation(console, self.rendered_lines, self.gradient, self.fps)
            elif self.animation == "fast_strobe":
                self._fast_strobe_animation(console, self.rendered_lines, self.gradient, self.fps)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(self.reported_width, options.max_width)

    ###########################
    # ~ Animation Functions ~ #
    ###########################

    # Background worker function to pre-render frames
    def _frame_worker(self, next_frame_callable: Callable[[], Lines | Panel]) -> None:
        while self.animation_running:
            if not self.frame_queue.full():
                next_frame = next_frame_callable()
                # self.previous_frame = next_frame
                self.frame_queue.put(next_frame)
            else:
                # Small sleep to prevent CPU hogging when queue is full
                time.sleep(0.01)

    def _get_renderable(self, next_frame_callable: Callable[[], Lines | Panel]) -> Lines | Panel:
        try:
            # Get the next pre-rendered frame from the queue
            return self.frame_queue.get(block=False)
        except Empty:
            # Safety fallback (shouldn't happen), make a frame on demand
            return next_frame_callable()

    def _vertical_animation(
        self,
        console: Console,
        rendered_lines: Lines,
        colors: list[Color],
        fps: float,
    ) -> None:
        self.position = 0
        self.animation_running = True
        if not self.border:
            rendered_lines.append(Text("\nPress ctrl+c to continue", style=Style(italic=True, dim=True)))

        self.frame_queue.put(rendered_lines)  # Initial render is the first frame

        def make_next_frame() -> Lines | Panel:

            for i, text_obj in enumerate(rendered_lines):
                if not self.border:
                    # If there's no border, it'll add an extra line at the end that says
                    # "Press ctrl+c to continue". So we want to skip coloring that line.
                    if i < len(rendered_lines) - 1:
                        color_index = (i + self.position) % len(colors)
                        text_obj.stylize(Style(color=colors[color_index]))

                # If there is a border, we don't need to add that last line,
                # since its already in the panel (below).
                else:
                    color_index = (i + self.position) % len(colors)
                    text_obj.stylize(Style(color=colors[color_index]))

            if self.border:
                panel = Panel(
                    rendered_lines,
                    box=BOXES[self.border],
                    padding=self.border_padding,
                    width=self.reported_width,
                    border_style=self.border_style_obj,
                    subtitle="Press ctrl+c to continue",
                    subtitle_align="left",
                )
                if self.animation == "gradient_up":
                    self.position += 1
                else:  # gradient_down
                    self.position -= 1
                return panel

            if self.animation == "gradient_up":
                self.position += 1
            else:  # gradient_down
                self.position -= 1
            return rendered_lines

        # Start the background worker thread
        worker_thread = threading.Thread(target=partial(self._frame_worker, make_next_frame), daemon=True)
        worker_thread.start()

        # Ensure the queue is full before proceeding
        while not self.frame_queue.full():
            time.sleep(0.01)

        with Live(
            console=console,
            refresh_per_second=fps,
            get_renderable=partial(self._get_renderable, make_next_frame),
        ) as live:

            try:
                while self.animation_running:
                    time.sleep(0.1)  # Keep the main thread alive

                    # The Live object runs its own loop in a separate thread to call _get_renderable.
                    # The main thread needs to stay alive for the animation to continue.
                    # This sleep does not control animation speed. It's just to prevent
                    # the while loop from spinning at 100% CPU.

            except KeyboardInterrupt:
                live.stop()
            finally:
                self.animation_running = False
                worker_thread.join(timeout=0.5)  # Make sure worker thread terminates

    def _smooth_strobe_animation(
        self,
        console: Console,
        rendered_lines: Lines,
        colors: list[Color],
        fps: float,
    ) -> None:
        self.position = 0
        self.animation_running = True
        if not self.border:
            rendered_lines.append(Text("\nPress ctrl+c to continue", style=Style(italic=True, dim=True)))

        # Create a queue to store pre-rendered frames
        self.frame_queue.put(rendered_lines)  # Initial render is the first frame

        def make_next_frame() -> Lines | Panel:

            color_index = self.position % len(colors)
            for i, text_obj in enumerate(rendered_lines):
                if not self.border:
                    if i < len(rendered_lines) - 1:  # dont color the last line
                        text_obj.stylize(Style(color=colors[color_index]))
                else:
                    text_obj.stylize(Style(color=colors[color_index]))

            if self.border:
                panel = Panel(
                    rendered_lines,
                    box=BOXES[self.border],
                    padding=self.border_padding,
                    width=self.reported_width,
                    border_style=self.border_style_obj,
                    subtitle="Press ctrl+c to continue",
                    subtitle_align="left",
                )
                self.position += 1
                return panel

            self.position += 1
            return rendered_lines

        # Start the background worker thread
        worker_thread = threading.Thread(target=partial(self._frame_worker, make_next_frame), daemon=True)
        worker_thread.start()

        # Ensure the queue is full before proceeding
        while not self.frame_queue.full():
            time.sleep(0.01)

        with Live(
            console=console,
            refresh_per_second=fps,
            get_renderable=partial(self._get_renderable, make_next_frame),
        ) as live:

            try:
                while self.animation_running:
                    time.sleep(0.1)  # Keep the main thread alive

                    # The Live object runs its own loop in a separate thread to call _get_renderable.
                    # The main thread needs to stay alive for the animation to continue.
                    # This sleep does not control animation speed. It's just to prevent
                    # the while loop from spinning at 100% CPU.

            except KeyboardInterrupt:
                live.stop()
            finally:
                self.animation_running = False
                worker_thread.join(timeout=0.5)  # Make sure worker thread terminates

    def _fast_strobe_animation(
        self,
        console: Console,
        rendered_lines: Lines,
        colors: list[Color],
        fps: float,
    ) -> None:
        self.position = 0
        self.animation_running = True
        if not self.border:
            rendered_lines.append(Text("\nPress ctrl+c to continue", style=Style(italic=True, dim=True)))

        # Create a queue to store pre-rendered frames
        self.frame_queue.put(rendered_lines)  # Initial render is the first frame

        def make_next_frame() -> Lines | Panel:

            color_index = self.position % len(colors)
            for i, text_obj in enumerate(rendered_lines):
                if not self.border:
                    if i < len(rendered_lines) - 1:  # dont color the last line
                        text_obj.stylize(Style(color=colors[color_index]))
                else:
                    text_obj.stylize(Style(color=colors[color_index]))

            if self.border:
                panel = Panel(
                    rendered_lines,
                    box=BOXES[self.border],
                    padding=self.border_padding,
                    width=self.reported_width,
                    border_style=self.border_style_obj,
                    subtitle="Press ctrl+c to continue",
                    subtitle_align="left",
                )
                self.position += 1
                return panel

            self.position += 1
            return rendered_lines

        # Start the background worker thread
        worker_thread = threading.Thread(target=partial(self._frame_worker, make_next_frame), daemon=True)
        worker_thread.start()

        # Ensure the queue is full before proceeding
        while not self.frame_queue.full():
            time.sleep(0.01)

        with Live(
            console=console,
            refresh_per_second=fps,
            get_renderable=partial(self._get_renderable, make_next_frame),
        ) as live:

            try:
                while self.animation_running:
                    time.sleep(0.1)  # Keep the main thread alive

                    # The Live object runs its own loop in a separate thread to call _get_renderable.
                    # The main thread needs to stay alive for the animation to continue.
                    # This sleep does not control animation speed. It's just to prevent
                    # the while loop from spinning at 100% CPU.

            except KeyboardInterrupt:
                live.stop()
            finally:
                self.animation_running = False
                worker_thread.join(timeout=0.5)  # Make sure worker thread terminates

    ##########################################################################

    # NOTE: The horizontal animation very unfortunately looks like crap.
    # I have no idea why, but Rich can't render it without glitching out.
    # I have tried everything I can think of to fix it, but nothing works.
    # I will leave this here for now, but it is not usable in its current state.

    # def make_next_frame() -> Lines:

    #     for i, text_obj in enumerate(rendered_lines):
    #         if i < len(rendered_lines) - 1:  # dont color the last line
    #             for j in range(len(text_obj)):
    #                 # Same index positions across all lines get the same color
    #                 color_index = (j + self.position) % len(colors)
    #                 text_obj.stylize(Style(color=colors[color_index]), j, j + 1)

    #     self.position += 1
    #     return rendered_lines
