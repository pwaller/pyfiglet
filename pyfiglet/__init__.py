#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Python FIGlet adaption
"""

from __future__ import print_function, unicode_literals

import os
import pkg_resources
import re
import shutil
import sys
import zipfile
from optparse import OptionParser

from .version import __version__

__author__ = "Peter Waller <p@pwaller.net>"
__copyright__ = """
The MIT License (MIT)
Copyright © 2007-2018
  Christopher Jones <cjones@insub.org>
  Stefano Rivera <stefano@rivera.za.net>
  Peter Waller <p@pwaller.net>
  And various contributors (see git history).

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


DEFAULT_FONT = "standard"

COLOR_CODES = {
    "BLACK": 30,
    "RED": 31,
    "GREEN": 32,
    "YELLOW": 33,
    "BLUE": 34,
    "MAGENTA": 35,
    "CYAN": 36,
    "LIGHT_GRAY": 37,
    "DEFAULT": 39,
    "DARK_GRAY": 90,
    "LIGHT_RED": 91,
    "LIGHT_GREEN": 92,
    "LIGHT_YELLOW": 93,
    "LIGHT_BLUE": 94,
    "LIGHT_MAGENTA": 95,
    "LIGHT_CYAN": 96,
    "WHITE": 97,
    "RESET": 0,
}

RESET_COLORS = b"\033[0m"

if sys.platform == "win32":
    SHARED_DIRECTORY = os.path.join(os.environ["APPDATA"], "pyfiglet")
else:
    SHARED_DIRECTORY = "/usr/local/share/pyfiglet/"


def figlet_format(text, font=DEFAULT_FONT, **kwargs):
    fig = Figlet(font, **kwargs)
    return fig.render_text(text)


def print_figlet(text, font=DEFAULT_FONT, colors=":", **kwargs):
    ansi_colors = parse_color(colors)
    if ansi_colors:
        sys.stdout.write(ansi_colors)

    print(figlet_format(text, font, **kwargs))

    if ansi_colors:
        sys.stdout.write(RESET_COLORS.decode("UTF-8", "replace"))
        sys.stdout.flush()


class FigletError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error


class CharNotPrinted(FigletError):
    """
    Raised when the width is not sufficient to print a character
    """


class FontNotFound(FigletError):
    """
    Raised when a font can't be located
    """


class FontError(FigletError):
    """
    Raised when there is a problem parsing a font file
    """


class InvalidColor(FigletError):
    """
    Raised when the color passed is invalid
    """


class FigletFont(object):
    """
    This class represents the currently loaded font, including
    meta-data about how it should be displayed by default
    """

    re_magic_number = re.compile(r"^[tf]lf2.")
    re_end_marker = re.compile(r"(.)\s*$")

    def __init__(self, font=DEFAULT_FONT):
        self.font = font

        self.comment = ""
        self.chars = {}
        self.width = {}
        self.data = self.preload_font(font)
        self.load_font()

    @classmethod
    def preload_font(cls, font):
        """
        Load font data if exist
        """
        # Find a plausible looking font file.
        data = None
        f = None
        for extension in ("tlf", "flf"):
            fn = "%s.%s" % (font, extension)
            if pkg_resources.resource_exists("pyfiglet.fonts", fn):
                f = pkg_resources.resource_stream("pyfiglet.fonts", fn)
                break
            else:
                for location in ("./", SHARED_DIRECTORY):
                    full_name = os.path.join(location, fn)
                    if os.path.isfile(full_name):
                        f = open(full_name, "rb")
                        break

        # Unzip the first file if this file/stream looks like a ZIP file.
        if f:
            if zipfile.is_zipfile(f):
                with zipfile.ZipFile(f) as zip_file:
                    zip_font = zip_file.open(zip_file.namelist()[0])
                    data = zip_font.read()
            else:
                # ZIP file check moves the current file pointer - reset to start of file.
                f.seek(0)
                data = f.read()

        # Return the decoded data (if any).
        if data:
            return data.decode("UTF-8", "replace")
        else:
            raise FontNotFound(font)

    @classmethod
    def is_valid_font(cls, font):
        if not font.endswith((".flf", ".tlf")):
            return False
        f = None
        full_file = os.path.join(SHARED_DIRECTORY, font)
        if os.path.isfile(font):
            f = open(font, "rb")
        elif os.path.isfile(full_file):
            f = open(full_file, "rb")
        else:
            f = pkg_resources.resource_stream("pyfiglet.fonts", font)

        if zipfile.is_zipfile(f):
            # If we have a match, the ZIP file spec says we should just read the first file in the ZIP.
            with zipfile.ZipFile(f) as zip_file:
                zip_font = zip_file.open(zip_file.namelist()[0])
                header = zip_font.readline().decode("UTF-8", "replace")
        else:
            header = f.readline().decode("UTF-8", "replace")

        f.close()

        return cls.re_magic_number.search(header)

    @classmethod
    def get_fonts(cls):
        all_files = pkg_resources.resource_listdir("pyfiglet", "fonts")
        if os.path.isdir(SHARED_DIRECTORY):
            all_files += os.listdir(SHARED_DIRECTORY)
        return [font.rsplit(".", 2)[0] for font in all_files if cls.is_valid_font(font)]

    @classmethod
    def info_font(cls, font, short=False):
        """
        Get informations of font
        """
        data = FigletFont.preload_font(font)
        infos = []
        re_start_marker = re.compile(
            r"""
            ^(FONT|COMMENT|FONTNAME_REGISTRY|FAMILY_NAME|FOUNDRY|WEIGHT_NAME|
              SETWIDTH_NAME|SLANT|ADD_STYLE_NAME|PIXEL_SIZE|POINT_SIZE|
              RESOLUTION_X|RESOLUTION_Y|SPACING|AVERAGE_WIDTH|
              FONT_DESCENT|FONT_ASCENT|CAP_HEIGHT|X_HEIGHT|FACE_NAME|FULL_NAME|
              COPYRIGHT|_DEC_|DEFAULT_CHAR|NOTICE|RELATIVE_).*""",
            re.VERBOSE,
        )
        re_end_marker = re.compile(r"^.*[@#$]$")
        for line in data.splitlines()[0:100]:
            if (
                cls.re_magic_number.search(line) is None
                and re_start_marker.search(line) is None
                and re_end_marker.search(line) is None
            ):
                infos.append(line)
        return "\n".join(infos) if not short else infos[0]

    @staticmethod
    def install_fonts(file_name):
        """
        Install the specified font file to this system.
        """
        if isinstance(
            pkg_resources.get_provider("pyfiglet"), pkg_resources.ZipProvider
        ):
            # Figlet is installed using a zipped resource - don't try to upload to it.
            location = SHARED_DIRECTORY
        else:
            # Figlet looks like a standard directory - so lets use that to install new fonts.
            location = pkg_resources.resource_filename("pyfiglet", "fonts")

        print("Installing {} to {}".format(file_name, location))

        # Make sure the required destination directory exists
        if not os.path.exists(location):
            os.makedirs(location)

        # Copy the font definitions - unpacking any zip files as needed.
        if os.path.splitext(file_name)[1].lower() == ".zip":
            # Ignore any structure inside the ZIP file.
            with zipfile.ZipFile(file_name) as zip_file:
                for font in zip_file.namelist():
                    font_file = os.path.basename(font)
                    if not font_file:
                        continue
                    with zip_file.open(font) as src:
                        with open(os.path.join(location, font_file), "wb") as dest:
                            shutil.copyfileobj(src, dest)
        else:
            shutil.copy(file_name, location)

    def load_font(self):
        """
        Parse loaded font data for the rendering engine to consume
        """
        try:
            # Parse first line of file, the header
            data = self.data.splitlines()

            header = data.pop(0)
            if self.re_magic_number.search(header) is None:
                raise FontError("%s is not a valid figlet font" % self.font)

            header = self.re_magic_number.sub("", header)
            header = header.split()

            if len(header) < 6:
                raise FontError("malformed header for %s" % self.font)

            hard_blank = header[0]
            height, base_line, max_length, old_layout, comment_lines = map(int, header[1:6])
            print_direction = full_layout = None

            # these are all optional for backwards compatibility
            if len(header) > 6:
                print_direction = int(header[6])
            if len(header) > 7:
                full_layout = int(header[7])

            # if the new layout style isn't available,
            # convert old layout style. backwards compatibility
            if full_layout is None:
                if old_layout == 0:
                    full_layout = 64
                elif old_layout < 0:
                    full_layout = 0
                else:
                    full_layout = (old_layout & 31) | 128

            # Some header information is stored for later, the rendering
            # engine needs to know this stuff.
            self.height = height
            self.hard_blank = hard_blank
            self.print_direction = print_direction
            self.smush_mode = full_layout

            # Strip out comment lines
            for i in range(0, comment_lines):
                self.comment += data.pop(0)

            def __char(data):
                """
                Function loads one character in the internal array from font
                file content
                """
                end = None
                width = 0
                chars = []
                for j in range(0, height):
                    line = data.pop(0)
                    if end is None:
                        end = self.re_end_marker.search(line).group(1)
                        end = re.compile(re.escape(end) + r"{1,2}\s*$")

                    line = end.sub("", line)

                    if len(line) > width:
                        width = len(line)
                    chars.append(line)
                return width, chars

            # Load ASCII standard character set (32 - 127)
            for i in range(32, 127):
                width, letter = __char(data)
                if "".join(letter) != "":
                    self.chars[i] = letter
                    self.width[i] = width

            # Load German Umlaut - the follow directly after standard character 127
            for i in "ÄÖÜäöüß":
                width, letter = __char(data)
                if "".join(letter) != "":
                    self.chars[ord(i)] = letter
                    self.width[ord(i)] = width

            # Load ASCII extended character set
            while data:
                line = data.pop(0).strip()
                i = line.split(" ", 1)[0]
                if i == "":
                    continue
                hex_match = re.search("^0x", i, re.IGNORECASE)
                if hex_match is not None:
                    i = int(i, 16)
                    width, letter = __char(data)
                    if "".join(letter) != "":
                        self.chars[i] = letter
                        self.width[i] = width

        except Exception as e:
            raise FontError("problem parsing %s font: %s" % (self.font, e))

    def __str__(self):
        return "<FigletFont object: %s>" % self.font


unicode_string = type("".encode("ascii").decode("ascii"))


class FigletString(unicode_string):
    """
    Rendered figlet font
    """

    # translation map for reversing ascii art / -> \, etc.
    __reverse_map__ = (
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
        " !\"#$%&')(*+,-.\\"
        "0123456789:;>=<?"
        "@ABCDEFGHIJKLMNO"
        "PQRSTUVWXYZ]/[^_"
        "`abcdefghijklmno"
        "pqrstuvwxyz}|{~\x7f"
        "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
        "\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
        "\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf"
        "\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
        "\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf"
        "\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
        "\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef"
        "\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
    )

    # translation map for flipping ascii art ^ -> v, etc.
    __flip_map__ = (
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
        " !\"#$%&'()*+,-.\\"
        "0123456789:;<=>?"
        "@VBCDEFGHIJKLWNO"
        "bQbSTUAMXYZ[/]v-"
        "`aPcdefghijklwno"
        "pqrstu^mxyz{|}~\x7f"
        "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
        "\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
        "\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf"
        "\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
        "\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf"
        "\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
        "\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef"
        "\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
    )

    def reverse(self):
        out = []
        for row in self.splitlines():
            out.append(row.translate(self.__reverse_map__)[::-1])

        return self.new_from_list(out)

    def flip(self):
        out = []
        for row in self.splitlines()[::-1]:
            out.append(row.translate(self.__flip_map__))

        return self.new_from_list(out)

    # doesn't do self.strip() because it could remove leading whitespace on first line of the font
    # doesn't do row.strip() because it could remove empty lines within the font character
    def strip_surrounding_newlines(self):
        out = []
        chars_seen = False
        for row in self.splitlines():
            # if the row isn't empty or if we're in the middle of the font character, add the line.
            if row.strip() != "" or chars_seen:
                chars_seen = True
                out.append(row)

        # rstrip to get rid of the trailing newlines
        return self.new_from_list(out).rstrip()

    def normalize_surrounding_newlines(self):
        return "\n" + self.strip_surrounding_newlines() + "\n"

    def new_from_list(self, list):
        return FigletString("\n".join(list) + "\n")


class FigletRenderingEngine(object):
    """
    This class handles the rendering of a FigletFont,
    including smushing/kerning/justification/direction
    """

    def __init__(self, base=None):
        self.base = base

    def render(self, text):
        """
        Render an ASCII text string in figlet
        """
        builder = FigletBuilder(
            text,
            self.base.Font,
            self.base.direction,
            self.base.width,
            self.base.justify,
        )

        while builder.is_not_finished():
            builder.add_char_to_product()
            builder.go_to_next_char()

        return builder.return_product()


class FigletProduct(object):
    """
    This class stores the internal build part of
    the ascii output string
    """

    def __init__(self):
        self.queue = list()
        self.buffer_string = ""

    def append(self, buffer):
        self.queue.append(buffer)

    def get_string(self):
        return FigletString(self.buffer_string)


class FigletBuilder(object):
    """
    Represent the internals of the build process
    """

    def __init__(self, text, font, direction, width, justify):

        self.text = list(map(ord, list(text)))
        self.direction = direction
        self.width = width
        self.font = font
        self.justify = justify

        self.iterator = 0
        self.max_smush = 0
        self.newBlankRegistered = False

        self.cur_char_width = 0
        self.prev_char_width = 0
        self.current_total_width = 0

        self.blank_markers = list()
        self.product = FigletProduct()
        self.buffer = ["" for i in range(self.font.height)]

        # constants.. lifted from figlet222
        self.SM_EQUAL = 1  # smush equal chars (not hardblanks)
        self.SM_LOWLINE = 2  # smush _ with any char in hierarchy
        self.SM_HIERARCHY = 4  # hierarchy: |, /\, [], {}, (), <>
        self.SM_PAIR = 8  # hierarchy: [ + ] -> |, { + } -> |, ( + ) -> |
        self.SM_BIGX = 16  # / + \ -> X, > + < -> X
        self.SM_HARDBLANK = 32  # hardblank + hardblank -> hardblank
        self.SM_KERN = 64
        self.SM_SMUSH = 128

    # builder interface

    def add_char_to_product(self):
        cur_char = self.get_cur_char()

        # if the character is a newline, we flush the buffer
        if self.text[self.iterator] == ord("\n"):
            self.blank_markers.append(([row for row in self.buffer], self.iterator))
            self.handle_new_line()
            return None

        if cur_char is None:
            return
        if self.width < self.get_cur_width():
            raise CharNotPrinted("Width is not enough to print this character")
        self.cur_char_width = self.get_cur_width()
        self.max_smush = self.current_smush_amount(cur_char)

        self.current_total_width = len(self.buffer[0]) + self.cur_char_width - self.max_smush

        if self.text[self.iterator] == ord(" "):
            self.blank_markers.append(([row for row in self.buffer], self.iterator))

        if self.text[self.iterator] == ord("\n"):
            self.blank_markers.append(([row for row in self.buffer], self.iterator))
            self.handle_new_line()

        if self.current_total_width >= self.width:
            self.handle_new_line()
        else:
            for row in range(0, self.font.height):
                self.add_cur_char_row_to_buffer_row(cur_char, row)

        self.prev_char_width = self.cur_char_width

    def go_to_next_char(self):
        self.iterator += 1

    def return_product(self):
        """
        Returns the output string created by formatProduct
        """
        if self.buffer[0] != "":
            self.flush_last_buffer()
        self.format_product()
        return self.product.get_string()

    def is_not_finished(self):
        ret = self.iterator < len(self.text)
        return ret

    # private

    def flush_last_buffer(self):
        self.product.append(self.buffer)

    def format_product(self):
        """
        This create the output string representation from
        the internal representation of the product
        """
        string_acc = ""
        for buffer in self.product.queue:
            buffer = self.justify_string(self.justify, buffer)
            string_acc += self.replace_hardblanks(buffer)
        self.product.buffer_string = string_acc

    def get_char_at(self, i):
        if i < 0 or i >= len(list(self.text)):
            return None
        c = self.text[i]

        if c not in self.font.chars:
            return None
        else:
            return self.font.chars[c]

    def get_char_width_at(self, i):
        if i < 0 or i >= len(self.text):
            return None
        c = self.text[i]
        if c not in self.font.chars:
            return None
        else:
            return self.font.width[c]

    def get_cur_char(self):
        return self.get_char_at(self.iterator)

    def get_cur_width(self):
        return self.get_char_width_at(self.iterator)

    def get_left_smushed_char(self, i, add_left):
        idx = len(add_left) - self.max_smush + i
        if 0 <= idx < len(add_left):
            left = add_left[idx]
        else:
            left = ""
        return left, idx

    def current_smush_amount(self, cur_char):
        return self.smush_amount(self.buffer, cur_char)

    def update_smushed_char_in_left_buffer(self, add_left, idx, smushed):
        l = list(add_left)
        if idx < 0 or idx > len(l):
            return add_left
        l[idx] = smushed
        add_left = "".join(l)
        return add_left

    def smush_row(self, cur_char, row):
        add_left = self.buffer[row]
        add_right = cur_char[row]

        if self.direction == "right-to-left":
            add_left, add_right = add_right, add_left

        for i in range(0, self.max_smush):
            left, idx = self.get_left_smushed_char(i, add_left)
            right = add_right[i]
            smushed = self.smush_chars(left=left, right=right)
            add_left = self.update_smushed_char_in_left_buffer(add_left, idx, smushed)
        return add_left, add_right

    def add_cur_char_row_to_buffer_row(self, cur_char, row):
        add_left, add_right = self.smush_row(cur_char, row)
        self.buffer[row] = add_left + add_right[self.max_smush:]

    def cut_buffer_common(self):
        self.current_total_width = len(self.buffer[0])
        self.buffer = ["" for i in range(self.font.height)]
        self.blank_markers = list()
        self.prev_char_width = 0
        cur_char = self.get_cur_char()
        if cur_char is None:
            return
        self.max_smush = self.current_smush_amount(cur_char)

    def cut_buffer_at_last_blank(self, saved_buffer, saved_iterator):
        self.product.append(saved_buffer)
        self.iterator = saved_iterator
        self.cut_buffer_common()

    def cut_buffer_at_last_char(self):
        self.product.append(self.buffer)
        self.iterator -= 1
        self.cut_buffer_common()

    def blank_exist(self, last_blank):
        return last_blank != -1

    def get_last_blank(self):
        try:
            saved_buffer, saved_iterator = self.blank_markers.pop()
        except IndexError:
            return -1, -1
        return (saved_buffer, saved_iterator)

    def handle_new_line(self):
        saved_buffer, saved_iterator = self.get_last_blank()
        if self.blank_exist(saved_iterator):
            self.cut_buffer_at_last_blank(saved_buffer, saved_iterator)
        else:
            self.cut_buffer_at_last_char()

    def justify_string(self, justify, buffer):
        if justify == "right":
            for row in range(0, self.font.height):
                buffer[row] = (" " * (self.width - len(buffer[row]) - 1)) + buffer[row]
        elif justify == "center":
            for row in range(0, self.font.height):
                buffer[row] = (" " * int((self.width - len(buffer[row])) / 2)) + buffer[
                    row
                ]
        return buffer

    def replace_hardblanks(self, buffer):
        string = "\n".join(buffer) + "\n"
        string = string.replace(self.font.hard_blank, " ")
        return string

    def smush_amount(self, buffer=[], cur_char=[]):
        """
        Calculate the amount of smushing we can do between this char and the
        last If this is the first char it will throw a series of exceptions
        which are caught and cause appropriate values to be set for later.

        This differs from C figlet which will just get bogus values from
        memory and then discard them after.
        """
        if (self.font.smush_mode & (self.SM_SMUSH | self.SM_KERN)) == 0:
            return 0

        max_smush = self.cur_char_width
        for row in range(0, self.font.height):
            line_left = buffer[row]
            line_right = cur_char[row]
            if self.direction == "right-to-left":
                line_left, line_right = line_right, line_left

            linebd = len(line_left.rstrip()) - 1
            if linebd < 0:
                linebd = 0

            if linebd < len(line_left):
                ch1 = line_left[linebd]
            else:
                linebd = 0
                ch1 = ""

            charbd = len(line_right) - len(line_right.lstrip())
            if charbd < len(line_right):
                ch2 = line_right[charbd]
            else:
                charbd = len(line_right)
                ch2 = ""

            amt = charbd + len(line_left) - 1 - linebd

            if ch1 == "" or ch1 == " ":
                amt += 1
            elif ch2 != "" and self.smush_chars(left=ch1, right=ch2) is not None:
                amt += 1

            if amt < max_smush:
                max_smush = amt

        return max_smush

    def smush_chars(self, left="", right=""):
        """
        Given 2 characters which represent the edges rendered figlet
        fonts where they would touch, see if they can be smushed together.
        Returns None if this cannot or should not be done.
        """
        if left.isspace():
            return right
        if right.isspace():
            return left

        # Disallows overlapping if previous or current char has a width of 1 or
        # zero
        if (self.prev_char_width < 2) or (self.cur_char_width < 2):
            return

        # kerning only
        if (self.font.smush_mode & self.SM_SMUSH) == 0:
            return

        # smushing by universal overlapping
        if (self.font.smush_mode & 63) == 0:
            # Ensure preference to visible characters.
            if left == self.font.hard_blank:
                return right
            if right == self.font.hard_blank:
                return left

            # Ensures that the dominant (foreground)
            # fig-character for overlapping is the latter in the
            # user's text, not necessarily the rightmost character.
            if self.direction == "right-to-left":
                return left
            else:
                return right

        if self.font.smush_mode & self.SM_HARDBLANK:
            if left == self.font.hard_blank and right == self.font.hard_blank:
                return left

        if left == self.font.hard_blank or right == self.font.hard_blank:
            return

        if self.font.smush_mode & self.SM_EQUAL:
            if left == right:
                return left

        smushes = ()

        if self.font.smush_mode & self.SM_LOWLINE:
            smushes += (("_", r"|/\[]{}()<>"),)

        if self.font.smush_mode & self.SM_HIERARCHY:
            smushes += (
                ("|", r"|/\[]{}()<>"),
                (r"\/", "[]{}()<>"),
                ("[]", "{}()<>"),
                ("{}", "()<>"),
                ("()", "<>"),
            )

        for a, b in smushes:
            if left in a and right in b:
                return right
            if right in a and left in b:
                return left

        if self.font.smush_mode & self.SM_PAIR:
            for pair in [left + right, right + left]:
                if pair in ["[]", "{}", "()"]:
                    return "|"

        if self.font.smush_mode & self.SM_BIGX:
            if (left == "/") and (right == "\\"):
                return "|"
            if (right == "/") and (left == "\\"):
                return "Y"
            if (left == ">") and (right == "<"):
                return "X"
        return


class Figlet(object):
    """
    Main figlet class.
    """

    def __init__(self, font=DEFAULT_FONT, direction="auto", justify="auto", width=80):
        self.font = font
        self._direction = direction
        self._justify = justify
        self.width = width
        self.set_font()
        self.engine = FigletRenderingEngine(base=self)

    def set_font(self, **kwargs):
        if "font" in kwargs:
            self.font = kwargs["font"]

        self.Font = FigletFont(font=self.font)

    def get_direction(self):
        if self._direction == "auto":
            direction = self.Font.print_direction
            if direction == 0:
                return "left-to-right"
            elif direction == 1:
                return "right-to-left"
            else:
                return "left-to-right"

        else:
            return self._direction

    direction = property(get_direction)

    def get_justify(self):
        if self._justify == "auto":
            if self.direction == "left-to-right":
                return "left"
            elif self.direction == "right-to-left":
                return "right"

        else:
            return self._justify

    justify = property(get_justify)

    def render_text(self, text):
        # wrapper method to engine
        return self.engine.render(text)

    def get_fonts(self):
        return self.Font.get_fonts()


def color_to_ansi(color, is_background):
    if not color:
        return ""
    color = color.upper()
    if color.count(";") > 0 and color.count(";") != 2:
        raise InvalidColor("Specified color '{}' not a valid color in R;G;B format")
    elif color.count(";") == 0 and color not in COLOR_CODES:
        raise InvalidColor(
            "Specified color '{}' not found in ANSI COLOR_CODES list".format(color)
        )

    if color in COLOR_CODES:
        ansi_code = COLOR_CODES[color]
        if is_background:
            ansi_code += 10
    else:
        ansi_code = 48 if is_background else 38
        ansi_code = "{};2;{}".format(ansi_code, color)

    return "\033[{}m".format(ansi_code)


def parse_color(color):
    foreground, _, background = color.partition(":")
    return color_to_ansi(foreground, is_background=False) + color_to_ansi(background, is_background=True)


def main():
    parser = OptionParser(version=__version__, usage="%prog [options] [text..]")
    parser.add_option(
        "-f",
        "--font",
        default=DEFAULT_FONT,
        help="font to render with (default: %default)",
        metavar="FONT",
    )
    parser.add_option(
        "-D",
        "--direction",
        type="choice",
        choices=("auto", "left-to-right", "right-to-left"),
        default="auto",
        metavar="DIRECTION",
        help="set direction text will be formatted in " "(default: %default)",
    )
    parser.add_option(
        "-j",
        "--justify",
        type="choice",
        choices=("auto", "left", "center", "right"),
        default="auto",
        metavar="SIDE",
        help="set justification, defaults to print direction",
    )
    parser.add_option(
        "-w",
        "--width",
        type="int",
        default=80,
        metavar="COLS",
        help="set terminal width for wrapping/justification " "(default: %default)",
    )
    parser.add_option(
        "-r",
        "--reverse",
        action="store_true",
        default=False,
        help="shows mirror image of output text",
    )
    parser.add_option(
        "-n",
        "--normalize-surrounding-newlines",
        action="store_true",
        default=False,
        help="output has one empty line before and after",
    )
    parser.add_option(
        "-s",
        "--strip-surrounding-newlines",
        action="store_true",
        default=False,
        help="removes empty leading and trailing lines",
    )
    parser.add_option(
        "-F",
        "--flip",
        action="store_true",
        default=False,
        help="flips rendered output text over",
    )
    parser.add_option(
        "-l",
        "--list_fonts",
        action="store_true",
        default=False,
        help="show installed fonts list",
    )
    parser.add_option(
        "-i",
        "--info_font",
        action="store_true",
        default=False,
        help="show font's information, use with -f FONT",
    )
    parser.add_option(
        "-L",
        "--load",
        default=None,
        help="load and install the specified font definition",
    )
    parser.add_option(
        "-c",
        "--color",
        default=":",
        help="""prints text with passed foreground color,
                            --color=foreground:background
                            --color=:background\t\t\t # only background
                            --color=foreground | foreground:\t # only foreground
                            --color=list\t\t\t # list all colors
                            COLOR = list[COLOR] | [0-255];[0-255];[0-255] (RGB)""",
    )
    opts, args = parser.parse_args()

    if opts.list_fonts:
        print("\n".join(sorted(FigletFont.get_fonts())))
        exit(0)

    if opts.color == "list":
        print(
            "[0-255];[0-255];[0-255] # RGB\n" + "\n".join((sorted(COLOR_CODES.keys())))
        )
        exit(0)

    if opts.info_font:
        print(FigletFont.info_font(opts.font))
        exit(0)

    if opts.load:
        FigletFont.install_fonts(opts.load)
        exit(0)

    if len(args) == 0:
        parser.print_help()
        return 1

    if sys.version_info < (3,):
        args = [arg.decode("UTF-8") for arg in args]

    text = " ".join(args)

    f = Figlet(
        font=opts.font,
        direction=opts.direction,
        justify=opts.justify,
        width=opts.width,
    )

    r = f.render_text(text)
    if opts.reverse:
        r = r.reverse()
    if opts.flip:
        r = r.flip()
    if opts.strip_surrounding_newlines:
        r = r.strip_surrounding_newlines()
    elif opts.normalize_surrounding_newlines:
        r = r.normalize_surrounding_newlines()

    if sys.version_info > (3,):
        # Set stdout to binary mode
        sys.stdout = sys.stdout.detach()

    ansi_colors = parse_color(opts.color)
    if ansi_colors:
        sys.stdout.write(ansi_colors.encode("UTF-8"))

    sys.stdout.write(r.encode("UTF-8"))
    sys.stdout.write(b"\n")

    if ansi_colors:
        sys.stdout.write(RESET_COLORS)

    return 0


if __name__ == "__main__":
    sys.exit(main())
