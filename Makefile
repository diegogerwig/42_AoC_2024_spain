# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
STREAMLIT = streamlit
VENV = $(HOME)/.virtualenvs/42aoc
VENV_BIN = $(VENV)/bin
REQUIREMENTS = requirements.txt
APP = app.py
ANALYTICS_APP = ./analytics/analytics_viewer.py
CURRENT_DIR = $(shell pwd)

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
	@cd "$(CURRENT_DIR)" && PYTHONPATH="$(CURRENT_DIR)" $(VENV_BIN)/$(STREAMLIT) run "$(APP)"

clean:
	@echo "$(GREEN)Cleaning cache files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

local: clean install run

analytics: check-venv
	@echo "$(GREEN)Starting Analytics Dashboard...$(NC)"
	@if [ ! -d "analytics/analytics_data" ]; then \
		echo "$(YELLOW)Creating analytics data directory...$(NC)"; \
		mkdir -p analytics/analytics_data; \
	fi
	@if [ ! -d "analytics/logs" ]; then \
		echo "$(YELLOW)Creating analytics logs directory...$(NC)"; \
		mkdir -p analytics/logs; \
	fi
	@cd "$(CURRENT_DIR)" && PYTHONPATH="$(CURRENT_DIR)" $(VENV_BIN)/$(STREAMLIT) run "$(ANALYTICS_APP)"

.PHONY: help system-deps install run clean local check-venv