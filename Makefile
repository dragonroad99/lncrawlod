# Default task: init

ifeq ($(OS),Windows_NT)
	PIP := python -m pip
	VERSION := "Unavailable"
else
	PIP := python3 -m pip
	VERSION := $$(sed -n -E "s/__version__ = '(.+)'/\1/p" lncrawl/__version__.py)
endif

PYTHON := poetry run python
SOURCES := $(SOURCES) __main__.py


shell ::
	poetry shell -n

run ::
	$(PYTHON) __main__.py $(arg)

setup ::
	$(PIP) install --user -U poetry
	poetry install

requirements ::
	poetry lock
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	poetry export --dev -f requirements.txt -o dev-requirements.txt --without-hashes

format ::
	$(PYTHON) -m autopep8 -aaa --in-place --max-line-length=80 --recursive $(SOURCES)

lint ::
	$(PYTHON) -m mypy $(SOURCES)
	$(PYTHON) -m flake8 --count --ignore="E501 F401" --statistics $(SOURCES)
	$(PYTHON) -m flake8 --count --ignore="E501 F401" --exit-zero \
		--max-complexity=10 --max-line-length=120 --statistics $(SOURCES)

test :: requirements lint
	$(PYTHON) -m tox --parallel auto

watch ::
	@echo "--- Select recent changes and re-run tests ---"
	$(PYTHON) -m ptw -- --testmon

watch_retry ::
	@echo "--- Retry failed tests on every file change ---"
	$(PYTHON) -m py.test -n auto --forked --looponfail

ci ::
	@echo "--- Generate a test report ---"
	$(PYTHON) -m py.test -n 8 --forked --junitxml=report.xml

coverage ::
	@echo "--- Generate a test coverage ---"
	$(PYTHON) -m py.test --cov-config=.coveragerc --verbose \
		--cov-report=term --cov-report=xml --cov=$(SOURCES)
	$(PYTHON) -m coveralls

build :: lint
	@poetry build

publish :: clean build
	$(PIP) install 'twine>=1.5.0'
	twine upload dist/*

publish_test :: clean build
	$(PIP) install 'twine>=1.5.0'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

ifeq ($(OS),Windows_NT)
clean ::
	@DEL report.xml coverage.xml 2> nul | @REM
	@RD /S /Q build dist .eggs 2> nul | @REM
	@RD /S /Q .benchmarks .coverage .tox 2> nul | @REM
	@RD /S /Q lightnovel_crawler.egg-info 2> nul | @REM
	@FORFILES /S /M "__pycache__" /C "CMD /C RD /S /Q @path" 2> nul | @REM
else
clean ::
	@rm -rf coverage.xml report.xml
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .benchmarks .coverage .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +
endif
