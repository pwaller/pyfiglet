#!/usr/bin/env python

"""
Python FIGlet adaption
"""

import sys
from optparse import OptionParser
import os
import re

__version__ = '0.1'

__copyright__ = """
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
"""

class FigletError(Exception):
	def __init__(self, error):
		self.error = error

	def __str__(self):
		return self.error

class FontNotFound(FigletError):
	pass

class FontError(FigletError):
	pass


class FigletFont(object):
	def __init__(self, dir='.', font='standard'):
		self.dir = dir
		self.font = font

		self.comment = ''
		self.chars = {}

		self.reMagicNumber = re.compile(r'^flf2.')
		self.reEndMarker = re.compile(r'(.)\s*$')

		self.loadFont()


	def loadFont(self):
		fontPath = '%s/%s.flf' % (self.dir, self.font)
		if os.path.exists(fontPath) is False:
			raise FontNotFound, "%s doesn't exist" % fontPath

		try:
			fo = open(fontPath, 'rb')
		except Exception, e:
			raise FontError, "couldn't open %s: %s" % (fontPath, e)

		try:
			"""
			Parse first line of file, the header
			"""
			header = fo.readline().strip()
			if self.reMagicNumber.search(header) is None:
				raise FontError, '%s is not a valid figlet font' % fontPath

			header = self.reMagicNumber.sub('', header)
			header = header.split()
			
			if len(header) < 6:
				raise FontError, 'malformed header for %s' % fontPath

			hardBlank = header[0]
			height, baseLine, maxLength, oldLayout, commentLines = map(int, header[1:6])
			printDirection = fullLayout = codeTagCount = None

			# these are all optional for backwards compat
			if len(header) > 6: printDirection = int(header[6])
			if len(header) > 7: fullLayout = int(header[7])
			if len(header) > 8: codeTagCount = int(header[8])

			# useful for later
			self.height = height
			self.hardBlank = hardBlank
			self.printDirection = printDirection

			"""
			Strip out comment lines
			"""
			for i in range(0, commentLines):
				self.comment += fo.readline()

			"""
			Load characters
			"""
			for i in range(32, 127):
				end = None
				for j in range(0, height):
					line = fo.readline().rstrip()
					if end is None:
						end = self.reEndMarker.search(line).group(1)

					line = line.replace(end, '')

					if self.chars.has_key(i) is False:
						self.chars[i] = []

					self.chars[i].append(line)


		finally:
			fo.close()


	def __str__(self):
		return '<FigletFont object: %s>' % self.font


class Figlet(object):
	def __init__(self, dir='.', font='standard', direction='auto', justify='auto', width=80):
		self.dir = dir
		self.font = font
		self._direction = direction
		self._justify = justify
		self.width = width
		self.setFont()

	def setFont(self, **kwargs):
		if kwargs.has_key('dir'):
			self.dir = kwargs['dir']

		if kwargs.has_key('font'):
			self.font = kwargs['font']

		self.Font = FigletFont(dir=self.dir, font=self.font)

	def getDirection(self):
		if self._direction == 'auto':
			direction = self.Font.printDirection
			if direction == 0:
				return 'left-to-right'
			elif direction == 1:
				return 'right-to-left'
		else:
			return self._direction

	direction = property(getDirection)

	def getJustify(self):
		if self._justify == 'auto':
			if self.direction == 'left-to-right':
				return 'left'
			elif self.direction == 'right-to-left':
				return 'right'

		else:
			return self._justify

	justify = property(getJustify)


	def translate(self, text):
		text = text.expandtabs()
		if self.direction == 'right-to-left':
			text = text[::-1]

		font = self.Font
		chars = map(ord, list(text))
		buffer = ''
		for i in range(0, font.height):
			line = ''
			for char in chars:
				line += font.chars[char][i]

			line = line.replace(font.hardBlank, ' ')

			if self.justify == 'center':
				line = line.center(self.width)
			elif self.justify == 'right':
				line = line.rjust(self.width)


			buffer += '%s\n' % line

		
		return buffer




def main():
	parser = OptionParser(version=__version__, usage='%prog [options] text..')

	parser.add_option(	'-f', '--font', default='standard',
				help='font to render with (default: %default)', metavar='FONT' )

	parser.add_option(	'-d', '--fontdir', default='/usr/local/share/figlet',
				help='location of font files (default: %default)', metavar='DIR' )

	parser.add_option(	'-D', '--direction', type='choice', choices=('auto', 'left-to-right', 'right-to-left'),
				default='auto', metavar='DIRECTION',
				help='set direction text will be formatted in (default: %default)' )

	parser.add_option(	'-j', '--justify', type='choice', choices=('auto', 'left', 'center', 'right'),
				default='auto', metavar='SIDE',
				help='set justification, defaults to print direction' )

	parser.add_option(	'-w', '--width', type='int', default=80, metavar='COLS',
				help='set terminal width for wrapping/justification (default: %default)' )


	opts, args = parser.parse_args()

	if len(args) == 0:
		parser.print_help()
		return 1

	text = ' '.join(args)

	f = Figlet(dir=opts.fontdir, font=opts.font, direction=opts.direction, justify=opts.justify, width=opts.width)
	print f.translate(text)


	return 0

if __name__ == '__main__': sys.exit(main())
