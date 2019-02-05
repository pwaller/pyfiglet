all:
	@echo 'Run "make publish" to do "python setup.py sdist bdist_wheel upload"'

publish:
	python setup.py sdist bdist_wheel upload