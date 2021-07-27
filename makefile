.PHONY: clean init

init: clean
	pipenv install --dev

migrate:
	pipenv run python manage.py migrate

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name 'db.sqlite3' -exec rm -f {} \;