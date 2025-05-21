cs:
	flake8 .
black:
	black .


install:
	pip install -r requirements.txt

pkg:
	python -m poetry build

clean-dist:
	python -c "import shutil, os; shutil.rmtree('dist', ignore_errors=True); os.makedirs('dist', exist_ok=True)"
clear-dist: clean-dist
cln-dist: clean-dist
clr-dist: clean-dist

publish:
	python -c "import os;t=os.getenv('PYPI_TOKEN');__import__('subprocess').run(f'python -m twine upload dist/* -u __token__ -p {t}',shell=True)"

upload: publish
test:
	pytest --log-cli-level=INFO
tests: test