# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
STREAMLIT = streamlit
VENV = $(HOME)/.virtualenvs/42aoc
VENV_BIN = $(VENV)/bin
REQUIREMENTS = requirements.txt
SRC_DIR = src
APP = app.py
PYTHONPATH = $(PWD)

# Colors for pretty printing
GREEN = \033[0;32m
NC = \033[0m # No Color
RED = \033[0;31m
YELLOW = \033[1;33m

.DEFAULT_GOAL := help

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "$(YELLOW)make system-deps$(NC) - Install system dependencies (requires sudo)"
	@echo "$(YELLOW)make install$(NC)     - Create virtual environment and install dependencies"
	@echo "$(YELLOW)make run$(NC)         - Run the Streamlit application"
	@echo "$(YELLOW)make clean$(NC)       - Remove cache files"
	@echo "$(YELLOW)make test$(NC)        - Run tests with coverage"
	@echo "$(YELLOW)make format$(NC)      - Format code with black"
	@echo "$(YELLOW)make lint$(NC)        - Run pylint"
	@echo "$(YELLOW)make local$(NC)       - Clean, install and run"

system-deps:
	@echo "$(GREEN)Installing system dependencies...$(NC)"
	@if command -v apt-get >/dev/null; then \
		sudo apt-get update && sudo apt-get install -y python3-venv; \
	elif command -v brew >/dev/null; then \
		brew install python3; \
	else \
		echo "$(RED)Could not detect package manager. Please install python3-venv manually.$(NC)"; \
		exit 1; \
	fi

check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)Virtual environment not found. Creating...$(NC)"; \
		make install; \
	fi

install:
	@echo "$(GREEN)Creating virtual environment at $(VENV)...$(NC)"
	@mkdir -p $(HOME)/.virtualenvs
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(VENV_BIN)/$(PIP) install --upgrade pip
	@$(VENV_BIN)/$(PIP) install -r $(REQUIREMENTS)
	@echo "$(GREEN)Installation complete!$(NC)"

run: check-venv
	@echo "$(GREEN)Starting Streamlit application...$(NC)"
	@cd $(PWD) && PYTHONPATH=$(PWD) $(VENV_BIN)/$(STREAMLIT) run $(APP)

clean:
	@echo "$(GREEN)Cleaning cache files...$(NC)"
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf $(SRC_DIR)/__pycache__
	@rm -rf *.egg-info
	@rm -rf .coverage
	@find $(PWD)/$(SRC_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(PWD)/$(SRC_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

test: check-venv
	@echo "$(GREEN)Running tests...$(NC)"
	@$(VENV_BIN)/$(PIP) install pytest pytest-cov
	@PYTHONPATH=$(PWD) $(VENV_BIN)/pytest tests/ -v --cov=$(SRC_DIR) --cov-report=term-missing

format: check-venv
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(VENV_BIN)/$(PIP) install black
	@$(VENV_BIN)/black $(SRC_DIR) tests $(APP)

lint: check-venv
	@echo "$(GREEN)Running linter...$(NC)"
	@$(VENV_BIN)/$(PIP) install pylint
	@$(VENV_BIN)/pylint $(SRC_DIR)/*.py $(APP)

local: clean install run

.PHONY: help system-deps install run clean test format lint local check-venv