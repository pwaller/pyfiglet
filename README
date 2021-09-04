All of the documentation and the majority of the work done was by
    Christopher Jones (cjones@insub.org).
Packaged by Peter Waller <p@pwaller.net>,
various enhancements by Stefano Rivera <stefano@rivera.za.net>.

                        _|_|  _|            _|              _|
_|_|_|    _|    _|    _|            _|_|_|  _|    _|_|    _|_|_|_|
_|    _|  _|    _|  _|_|_|_|  _|  _|    _|  _|  _|_|_|_|    _|
_|    _|  _|    _|    _|      _|  _|    _|  _|  _|          _|
_|_|_|      _|_|_|    _|      _|    _|_|_|  _|    _|_|_|      _|_|
_|              _|                      _|
_|          _|_|                    _|_|


SYNOPSIS

        pyfiglet is a full port of FIGlet (http://www.figlet.org/) into pure
        python. It takes ASCII text and renders it in ASCII art fonts (like
        the title above, which is the 'block' font).

FAQ

        Q. Why? WHY?!
        A. I was bored. Really bored.

        Q. What the hell does this do that FIGlet doesn't?
        A. Not much, except allow your font collection to live
           in one big zipfile. The point of this code is to embed
           dynamic figlet rendering in Python without having to
           execute an external program, although it operates on the
           commandline as well.  See below for USAGE details. You can
           think of this as a python FIGlet driver.

        Q. Does this support kerning/smushing like FIGlet?
        A. Yes, yes it does. Output should be identical to FIGlet. If
           not, this is a bug, which you should report to me!

        Q. Can I use/modify/redstribute this code?
        A. Yes, under the terms of the MIT (see LICENSE below).

        Q. I improved this code, what should I do with it?
        A. You can submit changes to https://github.com/pwaller/pyfiglet/pulls.
           If you make changes to the kerning/mushing/rendering portion, PLEASE
           test it throroughly. The code is fragile and complex.

        Q. Where did my font go?
        A. It turns out that we didn't have distribution rights for some of the
           fonts and so we had to remove them.  Full details of the change and
           why we did it are in https://github.com/pwaller/pyfiglet/issues/59
           and https://github.com/pwaller/pyfiglet/issues/89.

        Q. Where can I find these and other fonts?
        A. Do a quick search for "figlet fonts" on your favourite search engine
           should give you what you need.  However, if you are looking for the
           specific removed fonts, please go to http://www.jave.de/figlet/fonts.html.

        Q. Why are some fonts missing in <my favourite> distribution?
        A. Some Linux distributions have very strict legal restrictions on what
           contributions they will take.  For these systems, we have divided the
           fonts into ones that have a clear redistribution license and those that
           don't.  These are the fonts-standard and fonts-contrib directories in
           this repository.

        Q. What about those other fonts?
        A. While there isn't a watertight case for the license, we believe that
           any legal constraint for these fonts has long expired and so they
           are public domain, so are continuing to redistribute via pypi.  If
           an owner of any of these fonts wants us to stop, please just
           raise an issue on https://github.com/pwaller/pyfiglet/issues
           proving your ownership and we will remove the requested fonts.

USAGE

        You can use pyfiglet in one of two ways. First, it operates on the
        commandline as C figlet does and supports most of the same options.
        Run with --help to see a full list of tweaks.  Mostly you will only
        use -f to change the font. It defaults to standard.flf.

        tools/pyfiglet 'text to render'

        Pyfiglet is also a library that can be used in python code:

        from pyfiglet import Figlet
        f = Figlet(font='slant')
        print f.renderText('text to render')

        If you have found some new fonts that you want to use, you can use the
        command line interface to install your font file as follows:

        pyfiglet -L <font file>

        The font file can be a ZIP file of lots of fonts or just a single font.
        Depending on how you installed pyfiglet, you may find that you need
        root access to install the font - e.g. `sudo pyfiglet -L <font file>`.

AUTHOR

        pyfiglet is a *port* of FIGlet, and much of the code is directly translated
        from the C source. I optimized some bits where I could, but because the smushing
        and kerning code is so incredibly complex, it was safer and easier to port the logic
        almost exactly.  Therefore, I can't really take much credit for authorship, just
        translation. The original authors of FIGlet are listed on their website  at
        http://www.figlet.org/.

        The Python port was done by Christopher Jones <cjones@insub.org> (http://gruntle.org/).
        It is currently maintained by Peter Waller (p@pwaller.net, github:pwaller)

        The toilet fonts (.tlf) were imported from toilet 0.3-1, by Sam Hocevar <sam@zoy.org>.

THANKS

        github:stefanor for various bug fixes and improvements and the debian packaging.

        Thanks to anyone who contributed an issue or code on github!

LICENSE

        The MIT License (MIT)
        Copyright © 2007-2018

          Christopher Jones <cjones@insub.org>
          Stefano Rivera <stefano@rivera.za.net>
          Peter Waller <p@pwaller.net>
          And various contributors (see git history).

        (see LICENSE for full details)

CHANGELOG

        2018-12-06 0.8.0
            #62 Change LICENSE to MIT
            #61 Provide font installation option (-L) and remove
                unlicenced fonts from the distribution

        2018-10-17 0.7.6

            #57 Implement colored print
            #53 Allow fonts to be specified by path

        2016-06-12 0.7.5

            #46 Add 100+ fonts from java.de figlet fonts collection v4.0
            #48 Include python3 in testing

        2015-05-27 0.7.4

            #43 Don't leak file handles

        2015-04-14 0.7.3

            #41 Add newline and text wrapping support

        2014-09-14 0.7.2

            #35 Add this CHANGELOG
            #36 Bug fix for #34 (broken --reverse and --flip)
                (reported "character mapping must return integer, None or unicode")

        2014-07-27 0.7.1

            #29 Fix for UTF8 regression
            #31 Add __main__ entry point
            #32 Pep8 the code and minor refactoring
            #33 Trove classifiers update

        2014-06-02 0.7

            #9  Add --list_fonts and --info_font
            #10 Add tools/pyfiglet_example for listing all fonts
            #11 Fix the pyfiglet command (had bad python path)
            #12 Pyflakes fixes
            #13 Configure Travis Continuous Integration
            #17 Documentation usage sample fix
            #19 Enable pyfiglet to use extended ASCII chars
            #20 Add two cyrillic fonts
            #21 Python 3 support
            #27 Code improvements
            #28 Human readable font list (-l)
