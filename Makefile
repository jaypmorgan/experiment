ENV=env
BIN=$(ENV)/bin

.PHONEY: venv
venv: requirements.txt
	if ! [ -d env ]; then python3 -m venv env; fi
	$(BIN)/pip install -Ur requirements.txt

.PHONY: build
build:
	$(BIN)/pip install -U build
	$(BIN)/python -m build

.PHONY: upload
upload:
	$(BIN)/pip install -U twine
	$(BIN)/python -m twine upload dist/*
