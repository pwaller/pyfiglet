import pytest

from pyfiglet import (
    InvalidColor,
    color_to_ansi,
    figlet_format,
    parse_color,
    print_figlet,
)


@pytest.mark.parametrize(
    "color",
    ["-1;0;0", "256;0;0", "0;999;0", "0;0;256", "a;b;c", "1;;3", "1;2;3;4", "1;2"],
)
@pytest.mark.parametrize("background", [False, True])
def test_invalid_rgb_is_rejected(color, background):
    with pytest.raises(InvalidColor):
        color_to_ansi(color, isBackground=background)


@pytest.mark.parametrize("color", ["0;0;0", "255;255;255", "12;34;56"])
@pytest.mark.parametrize("background", [False, True])
def test_valid_rgb_escape_and_rendering(color, background):
    code = 48 if background else 38
    assert color_to_ansi(color, isBackground=background) == f"\033[{code};2;{color}m"


def test_named_colors_and_combined_rgb():
    assert parse_color("RED:BLUE") == "\033[31m\033[44m"
    assert parse_color("1;2;3:4;5;6") == "\033[38;2;1;2;3m\033[48;2;4;5;6m"
    assert parse_color(":") == ""


def test_colored_figlet_output_preserves_art_and_resets(capsys):
    print_figlet("RL", colors="1;2;3:4;5;6")
    assert capsys.readouterr().out == (
        "\033[38;2;1;2;3m\033[48;2;4;5;6m" + figlet_format("RL") + "\n\033[0m"
    )
