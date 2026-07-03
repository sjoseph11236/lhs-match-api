.PHONY: install test

install:
	pip3 install -r requirements.txt

test:
	@PYTHONPATH=. python3 -m pytest tests/ -v