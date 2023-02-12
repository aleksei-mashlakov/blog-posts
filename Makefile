.PHONY: help create-venv isort black mypy test local-ci
.DEFAULT_GOAL := help
VENV=venv
PYTHON_BIN=$(VENV)/bin
SRC=src
NOTEBOOKS=notebooks
SHELL := /bin/bash
.ONESHELL:

create-venv:  ## Create virtual environment
	rm -rf venv
	python3 -m venv $(VENV)
	$(PYTHON_BIN)/pip install --upgrade pip
	$(PYTHON_BIN)/pip install -r ./environment/requirements.txt

activate-env: ## Activate virtual environment
	. $(PYTHON_BIN)/activate && exec bash;

update-conda:
	conda env update --file ./environment/conda_env.yaml --prune

isort:  ## Check formatting with isort
	$(PYTHON_BIN)/isort $(SRC) $(NOTEBOOKS) --check-only

black:  ## Check formatting with black
	$(PYTHON_BIN)/black $(SRC) $(NOTEBOOKS) --check

mypy:  ## Check typing with mypy
	$(PYTHON_BIN)/mypy $(SRC)

test:  ## Run unit tests
	echo “Testing ...”
	pytest src/tests -s

run-notebooks:
	export PYTHONPATH=$(pwd)
	jupyter lab &

notebook-clear-output:  ## Clear jupyter notebook output
	$(PYTHON_BIN)/jupyter nbconvert \
        --NbConvertApp.use_output_suffix=False \
        --NbConvertApp.export_format=notebook \
        --FilesWriter.build_directory= \
        --ClearOutputPreprocessor.enabled=True \
        --ClearMetadataPreprocessor.clear_cell_metadata=True \
        notebooks/*.ipynb

local-ci: isort black mypy test  ## Local CI

setup-pre-commit-hook:  ## Setup git pre-commit hook for local CI automation
	printf ‘#!/bin/sh\nmake local-ci || (echo “\nINFO: Use -n flag to skip CI pipeline” && false)' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

docs_view: ## View docs
	@echo View API documentation...
	pdoc src --http localhost:8080

docs_save: ## Save doc FilesWrite
	@echo Save documentation to docs...
	pdoc src -o docs

clean: ## Delete all compiled Python files
	find . -type f -name “*.py[co]” -delete
	find . -type d -name “__pycache__” -delete
	rm -rf .pytest_cache

help: ## Show this help
	@grep -E ‘^[a-zA-Z_-]+:.*?## .*$$’ $(MAKEFILE_LIST) | sort | awk ‘BEGIN {FS = “:.*?## “}; {printf “\033[36m%-30s\033[0m %s\n”, $$1, $$2}’