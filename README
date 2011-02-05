All of the documentation and the majority of the work done was by
    Christopher Jones (cjones@insub.org).
Packaged by Peter Waller <peter.waller@gmail.com>,
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
	A. Yes, under the terms of the GPL (see LICENSE below).

	Q. I improved this code, what should I do with it?
	A. You can mail patches to <cjones@insub.org>. Particularly bugfixes.
           If you make changes to the kerning/mushing/rendering portion, PLEASE
           test it throroughly. The code is fragile and complex.


USAGE

	You can use pyfiglet in one of two ways. First, it operates on the
	commandline as C figlet does and supports most of the same options.
	Run with --help to see a full list of tweaks.  Mostly you will only
	use -f to change the font. It defaults to standard.flf.

	./pyfiglet 'text to render'

	Pyfiglet is also a library that can be used in python code:

	from pyfiglet import Figlet
	f = Figlet(font='slant', dir='/usr/local/share/figlet') # or zipfile=PATH
	print f.renderText('text to render')


	pyfiglet also supports reading fonts from a zip archive. pyfiglet
	comes with a file called fonts.zip which includes all of the default
	fonts FIGlet comes with as well as the standard collection of user-
	contributed fonts. By default, pyfiglet uses this for fonts. Specifying
	a directory (on the commandline or in the Figlet() object) will override
	this behavior. You may also specify a zipfile to use with -z or zipfile=PATH
	in the Figlet() constructor.

	If you wish to add/remove fonts or create your own font package, be aware
	that there *must* be a folder in the root of the zipfile called "fonts". You
	can examine the bunlded fonts.zip to see how it should be packaged.


AUTHOR

	pyfiglet is a *port* of FIGlet, and much of the code is directly translated
	from the C source. I optimized some bits where I could, but because the smushing
	and kerning code is so incredibly complex, it was safer and easier to port the logic
	almost exactly.  Therefore, I can't really take much credit for authorship, just
	translation. The original authors of FIGlet are listed on their website  at
	http://www.figlet.org/.

	The Python port was done by Christopher Jones <cjones@insub.org> (http://gruntle.org/).

LICENSE

	Copyright (C) 2007 Christopher Jones <cjones@insub.org>

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

	(see LICENSE for full details)
