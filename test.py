#!/usr/bin/env python

import sys
from optparse import OptionParser
from pyfiglet import Figlet
from subprocess import Popen, STDOUT, PIPE

__version__ = '0.1'

def main():
	parser = OptionParser(version=__version__)

	parser.add_option(	'-s', '--show', action='store_true', default=False,
				help='pause at each failure and compare output (default: %default)',	)

	opts, args = parser.parse_args()

	f = Figlet(zipfile='fonts.zip')

	ok = 0
	fail = 0

	for font in f.getFonts():
		f.setFont(font=font)

		outputPyfiglet = f.renderText('test')

		p = Popen('figlet -d ./fonts -f %s test' % font, shell=True, bufsize=1, stdout=PIPE)
		outputFiglet = ''.join(p.stdout.readlines())
		p.stdout.close()
		p.wait()

		if outputPyfiglet == outputFiglet:
			print '[OK] %s' % font
			ok += 1
			continue

		print '[FAIL] %s' % font
		fail += 1

		if opts.show is True:
			print '[PYTHON] *** %s\n\n%s\n' % (font, outputPyfiglet)
			print '[FIGLET] *** %s\n\n%s\n' % (font, outputFiglet)
			raw_input()

	print 'OK = %d, FAIL = %d' % (ok, fail)

	return 0

if __name__ == '__main__': sys.exit(main())
