help:
	@echo "-------------------"
	@echo " rich-pyfiglet CLI"
	@echo "-------------------"
	@echo "Use 'just run-ex' to run the example script."
	@echo "For info on the CLI, use 'rich-pyfiglet --help'"
	@echo "If using uv, that would be 'uv run rich-pyfiglet --help'"
	@echo

# Install the package
install:
	uv sync
	
# Run the small example script
run-ex:
	uv run example/example.py

# Run the script to generate the fonts list.
make-list:
	uv run scripts/make_fonts_list.py

# Runs ruff, exits with 0 if no issues are found
lint:
	uv run ruff check src || (echo "Ruff found issues. Please address them." && exit 1)

# Runs mypy, exits with 0 if no issues are found
typecheck:
	uv run mypy src || (echo "Mypy found issues. Please address them." && exit 1)

# Runs black
format:
	uv run black src

# Runs ruff, mypy, and black
all-checks: lint typecheck format
	@echo "All pre-commit checks passed. You're good to publish."

# Remove the build and dist directories
clean:
	rm -rf build dist
	find . -name "*.pyc" -delete

# Remove tool caches
clean-caches:
	rm -rf .mypy_cache
	rm -rf .ruff_cache	

# Remove the virtual environment and lock file
del-env:
	rm -rf .venv
	rm -rf uv.lock

# Removes all environment and build stuff
reset: clean del-env install
	@echo "Environment reset."

# Runs all-checks and cleaning stages before building
build: all-checks clean
	uv build
	
# Runs build stage before publishing
publish: build
	uv publish	
#-------------------------------------------------------------------------------

# I made sure to preserve the original PyFiglet CLI.
# You can access the original CLI with the following command:
#$ uv run python -m rich_pyfiglet.pyfiglet

