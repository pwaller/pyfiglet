# -*- coding: utf-8; -*-
#
# Copyright (c) 2014 Georgi Valkov. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#   3. Neither the name of author nor the names of its contributors
#      may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GEORGI
# VALKOV BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# VENDOR REPOSITORY: https://github.com/gvalkov/optparse-pretty.git

__author__  = 'Georgi Valkov'
__version__ = '0.1.1'
__license__ = 'Revised BSD License'


"""
HelpFormatter classes for optparse:

  CompactHelpFormatter:
      A less verbose and neater looking optparse help formatter.

  CompactColorHelpFormatter:
     A less verbose and neater looking optparse help formatter that can
     colorize options and headings.

Usage:

   from optparse import OptionParser
   from optparse_mooi import *

   fmt = CompactHelpFormatter(
      metavar_format=' <{}>',
      metavar_column=None,
      option_separator=', ',
      align_long_opts=False,
      help_string_formatter=None,
      preformatted_description=True,
      preformatted_epilog=True
   )

   fmt = CompactColorHelpFormatter(
      heading_color='white-bold',
      usage_color='white-bold',
      shopt_color=None,
      lopt_color=None,
      description_color=None,
      epilog_color=None,
      metavar_color=None,
      help_color=None,
      option_colormap=None
   )

   parser = OptionParser(formatter=fmt)
"""

import os, re

from optparse import IndentedHelpFormatter
from functools import partial


class CompactHelpFormatter(IndentedHelpFormatter):
    """A less verbose and neater looking optparse help formatter."""

    def __init__(self,
                 metavar_format=' <{}>',
                 metavar_column=None,
                 option_separator=', ',
                 align_long_opts=False,
                 help_string_formatter=None,
                 preformatted_description=True,
                 preformatted_epilog=True,
                 *args, **kw):
        """
        :arg metavar_format:
             Evaluated as `metavar_format.format(metavar)` if string.
             If callable, evaluated as `metavar_format(metavar)`.

        :arg metavar_column:
             Column to which all metavars should be aligned.

        :arg option_separator:
             String between short and long option. E.g: ', ' -> '-f, --format'.

        :arg align_long_opts:
             Align all long options on the current indent level to the same
             column. For example:

                align_long_opts=False         align_long_opts=True
             --------------------------    --------------------------
             -h, --help  show this  ...    -h, --help  show this  ...
             --fast      avoid slow ...        --fast  avoid slow ...

        :arg help_string_format:
             Function to call to call on help string after expansion. Called
             as `help_string_format(help, option)`.

        :arg preformatted_description:
             If True, description will be displayed as-is, instead of
             text-wrapping it first.

        :arg preformatted_description:
             If True, epilog will be displayed as-is, instead of
             text-wrapping it first.

        :arg width:
             Maximum help message width. Defaults to 78 unless $COLUMNS is set.
        """

        if not callable(metavar_format):
            func = partial(format_option_metavar, fmt=metavar_format)
        else:
            func = metavar_format

        self.metavar_format   = func
        self.metavar_column   = metavar_column
        self.align_long_opts  = align_long_opts
        self.option_separator = option_separator
        self.help_string_formatter = help_string_formatter

        if 'width' not in kw:
            try:
                kw['width'] = int(os.environ['COLUMNS']) - 2
            except (KeyError, ValueError):
                kw['width'] = 78

        kw['max_help_position'] = kw.get('max_help_position', kw['width'])
        kw['indent_increment']  = kw.get('indent_increment', 1)
        kw['short_first']       = kw.get('short_first', 1)

        # leave full control of description and epilog to us
        self.preformatted_description = preformatted_description
        self.preformatted_epilog      = preformatted_epilog

        IndentedHelpFormatter.__init__(self, *args, **kw)

    def format_option_strings(self, option):
        opts = format_option_strings(
            option,
            self.metavar_format,
            self.option_separator,
            self.align_long_opts,
        )

        if not option.takes_value():
            return ''.join(opts)

        if not self.metavar_column:
            return ''.join(opts)

        # align metavar to self.metavar_column
        lpre = sum(len(i) for i in opts[:-1])
        lpre += self.current_indent * self.indent_increment
        opts.insert(-1, ' '*(self.metavar_column - lpre))
        return ''.join(opts)

    def expand_default(self, option):
        help = IndentedHelpFormatter.expand_default(self, option)
        if callable(self.help_string_formatter):
            return self.help_string_formatter(help, option)
        return help

    def format_usage(self, usage, raw=False):
        # If there is no description, ensure that there is only one
        # newline between the usage string and the first heading.

        msg = usage if raw else 'Usage: %s' % usage
        if self.parser.description:
            msg += '\n'

        return msg

    def format_heading(self, heading):
        if heading == 'Options':
            return '\n'

        return heading + ':\n'

    def format_description(self, description):
        if self.preformatted_description:
            return description if description else ''
        else:
            return IndentedHelpFormatter.format_description(self, description)

    def format_epilog(self, epilog):
        if self.preformatted_epilog:
            return epilog if epilog else ''
        else:
            return IndentedHelpFormatter.format_epilog(self, epilog)

def format_option_strings(option, metavar_format, separator, align_long_opts=False):
    opts = []

    if option._short_opts:
        opts.append(option._short_opts[0])

    if option._long_opts:
        opts.append(option._long_opts[0])

    if len(opts) > 1:
        opts.insert(1, separator)

    if not option._short_opts and align_long_opts:
        opts.insert(0, '  %*s' % (len(separator), ''))

    if option.takes_value():
        opts.append(metavar_format(option))

    return opts

def format_option_metavar(option, fmt):
    metavar = option.metavar or option.dest.lower()
    return fmt.format(metavar)

def get_optimal_max_help_position(formatter, parser):
    from itertools import chain
    max_width = 0

    options = [parser.option_list]
    if hasattr(parser, 'option_groups'):
        options.extend(i.option_list for i in parser.option_groups)

    for option in chain(*options):
        formatted = len(formatter.format_option_strings(option))
        max_width = formatted if formatted > max_width else max_width

    return max_width


class CompactColorHelpFormatter(CompactHelpFormatter):
    """
    A less verbose and neater looking optparse help formatter that can
    colorize options and headings. Works only on ANSI capable terminals.
    """

    def __init__(self,
                 heading_color='white-bold',
                 usage_color='white-bold',
                 shopt_color=None,
                 lopt_color=None,
                 description_color=None,
                 epilog_color=None,
                 metavar_color=None,
                 help_color=None,
                 option_colormap=None,
                 *args, **kw):
        """
        Accepts all arguments that `CompactHelpFormatter` accepts in
        addition to:

        :arg heading_color:
             Color to use for headings (such as group names).

        :arg usage_color:
             Color to use for the usage line.

        :arg shopt_color:
             COlor to use for all short options.

        :arg lopt_color:
             Color to use for all long options.

        :arg epilog_color:
             Color to use for the epilog section.

        :arg description_color:
             Color to use for the description secrion.

        :arg metavar_color:
             Color to use for all metavars.

        :arg help_color:
             Color to use for all help messages.

        :arg option_colormap:
             A mapping of option flags to colors. For example:

             option_colormap = {
                # -h, -v, -h in white, their long opt in green,
                # metavar in red and help message in bold red.
                ('-h', '-v', '-j'): ('white', 'green', 'red', 'red-bold'),

                # --quiet's help message in blue
                '--quiet': (None, None, None, 'blue'),
             }

             Keys are short or long opts, or a list of short or long
             opts. Values specify the color to be applied to the short
             opt, long opt, metavar and help message (in that order).

        Available colors:

            black, red, green, yellow, blue, purple, cyan, white

        Available modifiers:

            bold, underline

        Example color specifiers:

            red-bold, red-bold-underline, red-underline

        """

        # regex for stripping ansi escape codes from strings
        self.re_ansi = re.compile('\033\[([14];)?\d\d?m')

        colors = {
            'black':  '30', 'red':    '31',
            'green':  '32', 'yellow': '33',
            'blue':   '34', 'purple': '35',
            'cyan':   '36', 'white':  '37',
        }

        # color spec to partial(ansiwrap, ...)
        #   'white-bold' -> #(ansiwrap(37, %, True))
        #   'red'        -> #(ansiwrap(31, %))
        #   None         -> #(str(%))
        #   'red-bold-underline' -> #(ansiwrap(31, %, True, True))
        def _ansiwrap(color):
            if not color: return str
            spec = color.split('-')
            color = colors[spec[0]]
            bold, uline = 'bold' in spec, 'underline' in spec
            return partial(ansiwrap, color, bold=bold, underline=uline)

        self.heading_color = _ansiwrap(heading_color)
        self.shopt_color   = _ansiwrap(shopt_color)
        self.lopt_color    = _ansiwrap(lopt_color)
        self.usage_color   = _ansiwrap(usage_color)
        self.help_color    = _ansiwrap(help_color)
        self.metavar_color = _ansiwrap(metavar_color)
        self.epilog_color  = _ansiwrap(epilog_color)
        self.description_color  = _ansiwrap(description_color)

        self.colormap = {}

        # flatten all keys and ensure that values is a four element list
        option_colormap = option_colormap if option_colormap else {}
        for opts, val in option_colormap.items():
            f = [_ansiwrap(i) if i else None for i in val]
            f = f + [None] * (4 - len(f))

            if not isseq(opts):
                self.colormap[opts] = f
            else:
                for opt in opts:
                    self.colormap[opt] = f

        CompactHelpFormatter.__init__(self, *args, **kw)

    def format_option(self, option):
        result = CompactHelpFormatter.format_option(self, option)
        shopt, lopt, meta, help = find_color(option, self.colormap)

        if option._short_opts and (shopt or self.shopt_color):
            re_short = rx_short(option._short_opts)
            shopt = shopt or self.shopt_color
            result = re_short.sub(shopt(r'\1'), result, 0)

        if option._long_opts and (lopt or self.lopt_color):
            re_long = rx_long(option._long_opts)
            lopt = lopt or self.lopt_color
            result = re_long.sub(lopt(r'\1'), result, 0)

        if option.takes_value() and (meta or self.metavar_color):
            var  = self.metavar_format(option)
            meta = meta or self.metavar_color
            result = result.replace(var, meta(var), 1)

        if option.help and (help or self.help_color):
            l1 = '( %s.*$)(\s*^.*)*' % re.escape(option.help[:4])
            re_help = re.compile(l1, re.MULTILINE)
            help = help or self.help_color
            result = re_help.sub(help('\g<0>'), result)

        return result

    def format_heading(self, heading):
        if heading == 'Options':
            return '\n'

        heading = self.heading_color(heading)
        heading = CompactHelpFormatter.format_heading(self, heading)
        return heading

    def format_usage(self, usage):
        usage = self.usage_color('Usage: %s' % usage)
        usage = CompactHelpFormatter.format_usage(self, usage, True)
        return usage

    def format_description(self, description):
        description = self.description_color(description if description else '')
        return CompactHelpFormatter.format_description(self, description)

    def format_epilog(self, epilog):
        epilog = self.epilog_color(epilog if epilog else '')
        return CompactHelpFormatter.format_epilog(self, epilog)


# --- utility functions ---------------------------------------------
def find_color(option, cmap):
    g1 = (i for i in option._short_opts if i in cmap)
    g2 = (i for i in option._long_opts  if i in cmap)

    res = next(g1, None) or next(g2, None)
    return cmap.get(res, [None]*4)

def rx_short(it):
    rx = ''.join(i[1] for i in it)
    if rx:
        rx = '( -[%s])' % rx
        return re.compile(rx)

def rx_long(it):
    rx = '|'.join(i[2:] for i in it)
    if rx:
        rx = '(--%s)' % rx
    return re.compile(rx)

def ansiwrap(code, text, bold=True, underline=False):
    code = "4;%s" % code if underline else code
    code = "1;%s" % code if bold else code
    return "\033[%sm%s\033[0m" % (code, text)

def isseq(it):
    return isinstance(it, (list, tuple, set))


__all__  = (
    CompactHelpFormatter,
    CompactColorHelpFormatter,
)