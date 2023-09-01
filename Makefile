all:
	@echo 'Run "make clean" to remove artifacts from old builds'
	@echo 'Run "make minimal" to build a package compliant with Fedora licensing'
	@echo 'Run "make full" to build a full package complete with contributed fonts'
	@echo 'Run "make publish" to upload to pypi'

clean:
	rm -rf build/
	rm -rf pyfiglet/fonts/
	mkdir pyfiglet/fonts/

minimal:    clean
	cp pyfiglet/fonts-standard/* pyfiglet/fonts
	python3 -m build

full:    clean
	cp pyfiglet/fonts-standard/* pyfiglet/fonts
	cp pyfiglet/fonts-contrib/* pyfiglet/fonts
	python3 -m build

publish:
	python3 -m twine check dist/*
	python3 -m twine upload dist/*
