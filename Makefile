# Variables
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
UV := uv

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  init       - Initialize a new virtual environment with uv"
	@echo "  deps       - Install dependencies using uv"
	@echo "  run        - Run the main.py script using uv"
	@echo "  clean      - Remove virtual environment and generated files"
	@echo "  help       - Show this help message"

# Initialize a new virtual environment with uv
.PHONY: init
init:
	@echo "Initializing virtual environment with uv..."
	$(UV) venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

# Install dependencies using uv
.PHONY: deps
deps:
	@echo "Installing dependencies using uv..."
	$(UV) sync
	@echo "Dependencies installed"

# Run the main.py script using uv
.PHONY: run
run:
	@echo "Running main.py using uv..."
	$(UV) run main.py

# Clean up generated files and virtual environment
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	rm -f users_data.csv
	@echo "Cleanup complete"