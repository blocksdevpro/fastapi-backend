dev:
	uvicorn main:app --reload
start:
	uvicorn main:app --host 0.0.0.0 --port 8000
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	echo "- Cleaned Python cache files"
format:
	ruff check --fix && ruff format
	echo "- Code formatted"