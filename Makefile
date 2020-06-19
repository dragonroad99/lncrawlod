# Default task: init

ifeq ($(OS),Windows_NT)
	PIP := python -m pip
else
	PIP := python3 -m pip
endif

SOURCES := $(SOURCES) __main__.py

init ::
	poetry shell -n

run ::
	@poetry run python .

setup ::
	$(PIP) install --user -U poetry
	poetry install

requirements ::
	poetry lock
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	poetry export --dev -f requirements.txt -o dev-requirements.txt --without-hashes

format ::
	poetry run autopep8 -aaa --in-place --max-line-length=80 --recursive $(SOURCES)

lint ::
	poetry run mypy $(SOURCES)
	poetry run flake8 --count --ignore="E501 F401" --statistics $(SOURCES)
	poetry run flake8 --count --ignore="E501 F401" --exit-zero \
		--max-complexity=10 --max-line-length=120 --statistics $(SOURCES)

test ::
	make requirements lint
	poetry run tox --parallel auto

watch ::
	@echo "--- Select recent changes and re-run tests ---"
	poetry run ptw -- --testmon

watch_retry ::
	@echo "--- Retry failed tests on every file change ---"
	poetry run py.test -n auto --forked --looponfail

ci ::
	@echo "--- Generate a test report ---"
	poetry run py.test -n 8 --forked --junitxml=report.xml

coverage ::
	@echo "--- Generate a test coverage ---"
	poetry run py.test --cov-config=.coveragerc --verbose \
		--cov-report=term --cov-report=xml --cov=$(SOURCES)
	poetry run coveralls

build ::
	make lint
	poetry run python setup.py sdist bdist_wheel --universal

publish ::
	make build
	$(PIP) install 'twine>=1.5.0'
	twine upload dist/*

publish_test ::
	make build
	$(PIP) install 'twine>=1.5.0'
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

ifeq ($(OS),Windows_NT)
clean ::
	DEL report.xml coverage.xml 2> nul
	RD /S /Q build dist .tox .egg .mypy_cache 2> nul
	RD /S /Q lightnovel_crawler.egg-info 2> nul
	RD /S /Q $(shell dir "." /AD /B /S | findstr /E /I /R "__pycache__") 2> nul
else
clean ::
	rm -f report.xml coverage.xml
	rm -rf build dist .tox .egg *.egg-info .mypy_cache
	find "." -type d -name "__pycache__" | xargs rm -rf
endif
