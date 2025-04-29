install:
	poetry install

lint:
	poetry run black src/ tests/
	poetry run flake8 src/ tests/

typecheck:
	poetry run mypy src/ tests/

test:
	poetry run pytest tests/
