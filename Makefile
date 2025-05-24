cs:
	flake8 .
black:
	black .


install:
	pip install -e .

pkg:
	python multi-build.py
build: pkg

clear-dist:
	python -c "import shutil, os; shutil.rmtree('dist', ignore_errors=True); os.makedirs('dist', exist_ok=True)"
clr-dist: clear-dist

publish:
	python -c "import os;t=os.getenv('PYPI_TOKEN');__import__('subprocess').run(f'python -m twine upload dist/* -u __token__ -p {t}',shell=True)"

upload: publish
test:
	pytest --log-cli-level=INFO
tests: test