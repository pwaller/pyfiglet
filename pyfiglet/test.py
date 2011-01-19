#!/usr/bin/env python

import sys
from optparse import OptionParser
from pyfiglet import Figlet
from subprocess import Popen, STDOUT, PIPE

__version__ = '0.1'

def dump(text):
	for line in text.split('\n'):
		print repr(line)

def main():
	parser = OptionParser(version=__version__)

	parser.add_option(	'-s', '--show', action='store_true', default=False,
				help='pause at each failure and compare output (default: %default)',	)

	opts, args = parser.parse_args()

	f = Figlet()

	ok = 0
	fail = 0
	failed = []
	skip = ['runic'] # known bug..

	for font in f.getFonts():
		if font in skip: continue

		f.setFont(font=font)

		outputPyfiglet = f.renderText('foo')

		p = Popen('figlet -d ./fonts -f %s foo' % font, shell=True, bufsize=1, stdout=PIPE)
		outputFiglet = ''.join(p.stdout.readlines())
		p.stdout.close()
		p.wait()

		if outputPyfiglet == outputFiglet:
			print '[OK] %s' % font
			ok += 1
			continue

		print '[FAIL] %s' % font
		fail += 1
		failed.append(font)

		if opts.show is True:
			print '[PYTHON] *** %s\n\n' % font
			dump(outputPyfiglet)
			print '[FIGLET] *** %s\n\n' % font
			dump(outputFiglet)
			raw_input()

	print 'OK = %d, FAIL = %d' % (ok, fail)
	if len(failed) > 0:
		print 'FAILED = %s' % repr(failed)

	return 0

if __name__ == '__main__': sys.exit(main())
