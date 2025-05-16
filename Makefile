cs:
	flake8 .
black:
	black .
# ============== [ Tests ] ==============


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
	python publish.py

upload: publish