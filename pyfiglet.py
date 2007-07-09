#!/usr/bin/env python

"""
Python FIGlet adaption
"""

import sys
from optparse import OptionParser
import os
import re
from zipfile import ZipFile

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
		self.width = {}
		self.data = None

		self.reMagicNumber = re.compile(r'^flf2.')
		self.reEndMarker = re.compile(r'(.)\s*$')

		self.readFontFile()
		self.loadFont()

	def readFontFile(self):
		fontPath = '%s/%s.flf' % (self.dir, self.font)
		if os.path.exists(fontPath) is False:
			raise FontNotFound, "%s doesn't exist" % fontPath

		try:
			fo = open(fontPath, 'rb')
		except Exception, e:
			raise FontError, "couldn't open %s: %s" % (fontPath, e)

		try: self.data = fo.read()
		finally: fo.close()


	def loadFont(self):
		try:
			"""
			Parse first line of file, the header
			"""
			data = self.data.splitlines()

			header = data.pop(0)
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

			if fullLayout is None:
				if oldLayout == 0:
					fullLayout = 64
				elif oldLayout < 0:
					fullLayout = 0
				else:
					fullLayout = (oldLayout & 31) | 128



			# useful for later
			self.height = height
			self.hardBlank = hardBlank
			self.printDirection = printDirection
			self.smushMode = fullLayout

			"""
			Strip out comment lines
			"""
			for i in range(0, commentLines):
				self.comment += data.pop(0)

			"""
			Load characters
			"""
			for i in range(32, 127):
				end = None
				width = 0
				for j in range(0, height):
					line = data.pop(0)
					if end is None:
						end = self.reEndMarker.search(line).group(1)

					line = line.replace(end, '')

					if len(line) > width:
						width = len(line)

					if self.chars.has_key(i) is False:
						self.chars[i] = []

					self.chars[i].append(line)

				self.width[i] = width


		except Exception, e:
			raise FontError, 'problem parsing %s font: %s' % (self.font, e)


	def __str__(self):
		return '<FigletFont object: %s>' % self.font



class ZippedFigletFont(FigletFont):
	def __init__(self, dir='.', font='standard', zipfile='fonts.zip'):
		self.zipfile = zipfile
		FigletFont.__init__(self, dir=dir, font=font)

	def readFontFile(self):
		if os.path.exists(self.zipfile) is False:
			raise FontNotFound, "%s doesn't exist" % self.zipfile

		fontPath = 'fonts/%s.flf' % self.font

		try:
			z = ZipFile(self.zipfile, 'r')
			files = z.namelist()
			if fontPath not in files:
				raise FontNotFound, '%s not found in %s' % (self.font, self.zipfile)

			self.data = z.read(fontPath)

		except Exception, e:
			raise FontError, "couldn't open %s: %s" % (fontPath, e)



"""
This class handles the dirty bits of kerning/smushing
"""
class FigletRenderingEngine(object):
	def __init__(self, base=None):
		self.base = base

		self.prevCharWidth = 100
		self.curCharWidth = 100

		# constants
		self.SM_EQUAL = 1	# smush equal chars (not hardblanks)
		self.SM_LOWLINE = 2	# smush _ with any char in hierarchy
		self.SM_HIERARCHY = 4	# hierarchy: |, /\, [], {}, (), <>
		self.SM_PAIR = 8	# hierarchy: [ + ] -> |, { + } -> |, ( + ) -> |
		self.SM_BIGX = 16	# / + \ -> X, > + < -> X
		self.SM_HARDBLANK = 32	# hardblank + hardblank -> hardblank
		self.SM_KERN = 64
		self.SM_SMUSH = 128


	"""
	This is almost a direct translation from smushem() in
	FIGlet222. Could possibly be done more efficiently with
	Python idioms if anyone cares to undertake it. That wouldn't be I.
	"""
	def smushChars(self, left='', right=''):

		if left.isspace() is True: return right
		if right.isspace() is True: return left

		# Disallows overlapping if previous or current char has a width of 1 or zero
		if (self.prevCharWidth < 2) or (self.curCharWidth < 2): return
		print '[SMUSH] A'

		# kerning only
		if (self.base.Font.smushMode & self.SM_SMUSH) == 0: return
		print '[SMUSH] B'
		# smushing by universal overlapping
		if (self.base.Font.smushMode & 63) == 0:
			# Ensure preference to visiable characters.
			if left == self.base.Font.hardBlank: return right
			if right == self.base.Font.hardBlank: return left

			"""
			Ensures that the dominant (foreground)
			fig-character for overlapping is the latter in the
			user's text, not necessarily the rightmost character.
			"""
			if self.base.direction == 'right-to-left': return left
			else: return right

		if self.base.Font.smushMode & self.SM_HARDBLANK:
			if left == self.base.Font.hardBlank and right == self.base.Font.hardBlank:
				return left

		if left == self.base.Font.hardBlank or right == self.base.Font.hardBlank:
			return
		print '[SMUSH] C'

		if self.base.Font.smushMode & self.SM_EQUAL:
			if left == right:
				return left

		if self.base.Font.smushMode & self.SM_LOWLINE:
			if (left  == '_') and (right in r'|/\[]{}()<>'): return right
			if (right == '_') and (left  in r'|/\[]{}()<>'): return left

		if self.base.Font.smushMode & self.SM_HIERARCHY:
			if (left  == '|')   and (right in r'|/\[]{}()<>'): return right
			if (right == '|')   and (left  in r'|/\[]{}()<>'): return left
			if (left  in r'\/') and (right in '[]{}()<>'): return right
			if (right in r'\/') and (left  in '[]{}()<>'): return left
			if (left  in '[]')  and (right in '{}()<>'): return right
			if (right in '[]')  and (left  in '{}()<>'): return left
			if (left  in '{}')  and (right in '()<>'): return right
			if (right in '{}')  and (left  in '()<>'): return left
			if (left  in '()')  and (right in '<>'): return right
			if (right in '()')  and (left  in '<>'): return left

		if self.base.Font.smushMode & self.SM_PAIR:
			for pair in [left+right, right+left]:
				if pair in ['[]', '{}', '()']: return '|'

		if self.base.Font.smushMode & self.SM_BIGX:
			if (left == '/') and (right == '\\'): return '|'
			if (right == '/') and (left == '\\'): return 'Y'
			if (left == '>') and (right == '<'): return 'X'

		print '[SMUSH] D'
		return



	"""
	Render an ASCII text string in figlet
	"""
	def render(self, text):
		curCharWidth = 0
		buffer = ['' for i in range(0, self.base.Font.height)]

		for c in map(ord, list(text)):
			print "* Current Char: '%s'" % chr(c)
			curChar = self.base.Font.chars[c]
			prevCharWidth = curCharWidth
			curCharWidth = self.base.Font.width[c]
			print "   => prevCharWidth = %d" % prevCharWidth
			print "   => currCharWidth = %d" % curCharWidth

			""" this is missing.. hrm
			  if ((smushmode & (SM_SMUSH | SM_KERN)) == 0) {
			      return 0;
			          }"""

			print '>>>>>>>>>> calculating maxSmush <<<<<<<<<<'

			maxSmush = curCharWidth
			print "* initial set to: %d" % maxSmush
			for row in range(0, self.base.Font.height):
				print "(WANT TO ADD) '%s'" % curChar[row]
				print '*** row = %d' % row
				print 'dir = %s' % self.base.direction
				if self.base.direction == 'left-to-right':
					try:
						print "LOL: '%s'" % buffer[row]
						linebd = len(buffer[row].rstrip()) - 1
						if linebd < 0: linebd = 0
						ch1 = buffer[row][linebd]
					except:
						linebd = 0
						ch1 = ''


					print 'linebd = %s, ch1 = \'%s\'' % (linebd, ch1)

					try:
						charbd = len(curChar[row]) - len(curChar[row].lstrip())
						ch2 = curChar[row][charbd]
					except:
						charbd = len(curChar[row])
						ch2 = ''
						
					print "charbd = %s, ch2 = '%s'" % (charbd, ch2)

					#print 'charbd = %s' % charbd
					#print "'%s'" % ch2

					try: curLength = len(buffer[row])
					except: curLength = 0

					#print 'outlinelen = %d' % curLength

					amt = charbd + curLength-1-linebd
					print 'initial amt = %d' % amt
					#print 'amt = %d' % amt

					if ch1 == '' or ch1 == ' ':
						print "(*) LOGIC A TRIGGER"
						amt += 1
					elif ch2 != '':
						if self.smushChars(left=ch1, right=ch2) is not None:
							print "(*) LOGIC B TRIGGER"
							amt += 1

					print 'amt after logic = %d' % amt
					#print 'amt = %d' % amt

					if amt < maxSmush:
						maxSmush = amt

			print "      ((( maxsmush = %d )))" % maxSmush


			for row in range(0, self.base.Font.height):
				print '[RENDER] row = %d' % row
				wBuffer = buffer[row]
				wChar = curChar[row]
				for i in range(0, maxSmush):
					print '[RENDER-FOR2] k = %d' % i

					# XXX this is the broken part.. fencepost?
					print "[RENDER-FOR2] buffer = '%s'" % wBuffer
					print "[RENDER-FOR2] newchr = '%s'" % wChar


					indA = len(wBuffer) - maxSmush + i


					# this excepts
					try: left = wBuffer[indA]
					except: left = ''

					right = wChar[i]
					print "[RENDER-FOR2] left = '%s'" % left
					print "[RENDER-FOR2] right = '%s'" % right
					smushed = self.smushChars(left=left, right=right)
					print "[RENDER-FOR2] smushChar = '%s'" % smushed
					#smushed = self.smushChars(left=left, right=right)

					l = list(wBuffer)
					sind = len(l)-maxSmush+i
					print "%d - %d + %d = %d" % ( len(l), maxSmush, i, sind)
					print "Index of part being replaced is %d" % sind

					try:
						if smushed is not None:
							l = list(wBuffer)
							l[sind] = smushed
							wBuffer = ''.join(l)
					except: pass

				print '(done with smushing, add new char'
				wBuffer += wChar[maxSmush:]
				buffer[row] = wBuffer



			if len(buffer[0]) == 0: buffer = curChar
			print '\n\n<<< RESULT AFTER ITER >>>\n'
			for row in range(0, self.base.Font.height):
				print "* '%s'" % buffer[row]





		buffer = '\n'.join(buffer)
		buffer = buffer.replace(self.base.Font.hardBlank, ' ')
		return buffer



"""
Main figlet class.
"""
class Figlet(object):
	def __init__(self, dir=None, zipfile=None, font='standard', direction='auto', justify='auto', width=80):
		self.dir = dir
		self.font = font
		self._direction = direction
		self._justify = justify
		self.width = width
		self.zipfile = zipfile
		self.setFont()
		self.engine = FigletRenderingEngine(base=self)


	def setFont(self, **kwargs):
		if kwargs.has_key('dir'):
			self.dir = kwargs['dir']

		if kwargs.has_key('font'):
			self.font = kwargs['font']

		if kwargs.has_key('zipfile'):
			self.zipfile = kwargs['zipfile']


		Font = None
		if self.zipfile is not None:
			try: Font = ZippedFigletFont(dir=self.dir, font=self.font, zipfile=self.zipfile)
			except: pass

		if Font is None and self.dir is not None:
			try: Font = FigletFont(dir=self.dir, font=self.font)
			except: pass

		if Font is None:
			raise FontNotFound, "Couldn't load font %s: Not found" % self.font

		self.Font = Font


	def getDirection(self):
		if self._direction == 'auto':
			direction = self.Font.printDirection
			if direction == 0:
				return 'left-to-right'
			elif direction == 1:
				return 'right-to-left'
			else:
				return 'left-to-right'

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

	def renderText(self, text):
		return self.engine.render(text)





def main():
	dir = os.path.abspath(os.path.dirname(sys.argv[0]))

	parser = OptionParser(version=__version__, usage='%prog [options] text..')

	parser.add_option(	'-f', '--font', default='standard',
				help='font to render with (default: %default)', metavar='FONT' )

	parser.add_option(	'-d', '--fontdir', default=None,
				help='location of font files', metavar='DIR' )

	parser.add_option(	'-z', '--zipfile', default=dir+'/fonts.zip',
				help='specify a zipfile to use instead of a directory of fonts' )

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

	f = Figlet(
		dir=opts.fontdir, font=opts.font, direction=opts.direction,
		justify=opts.justify, width=opts.width, zipfile=opts.zipfile,
	)

	print f.renderText(text)


	return 0

if __name__ == '__main__': sys.exit(main())
