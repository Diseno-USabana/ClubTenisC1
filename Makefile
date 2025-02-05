.DEFAULT_GOAL := help

VENV_DIR ?= .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
VENV_RUN = . $(VENV_ACTIVATE);

.SILENT:

.env:
	cp .sample.env .env

$(VENV_DIR):
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)

.PHONY:

envsetup: .env $(VENV_DIR)
	$(VENV_RUN) pip install --upgrade pip
	$(VENV_RUN) pip install -r requirements.txt
	$(VENV_RUN) pre-commit install

docker-build: ## Build the Docker image
	docker compose build

docker-up: ## Start the server in a Docker container
	docker compose up -d

docker-down: ## Stop the Docker server
	docker compose down

docker-shell: ## Start a shell in the Docker container
	docker compose exec -it web /bin/bash

test: ## Run tests in the Docker container
	$(VENV_RUN) python manage.py test

lint: $(VENV_DIR) ## Run linters via pre-commit
	$(VENV_RUN) pre-commit run --all-files
	npx prettier frontend/ --write

help: ## Show this help message
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
