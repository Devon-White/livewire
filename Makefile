.PHONY: install start lint format clean replit-setup dev-install dev docs

install:
	pip install -r requirements.txt 

# For Replit: install dependencies and start the application
replit-setup:
	pip install -r requirements.txt
	python src/livewire/app.py

# Start the application
start:
	python src/livewire/app.py

# Start the application in development mode with auto-reload
dev:
	FLASK_DEBUG=True python src/livewire/app.py

# Install development dependencies
dev-install:
	pip install -r requirements.txt
	pip install black isort pytest

# Run linting
lint:
	black src/livewire
	isort src/livewire

# Format code
format: lint

# Clean up temporary files
clean:
	python -c "import shutil, os; [shutil.rmtree(root, ignore_errors=True) for root, dirs, files in os.walk('.', topdown=False) if os.path.basename(root) == '__pycache__']"

# Generate documentation for key components
docs:
	@echo "============================================================"
	@echo "Project Structure Documentation"
	@echo "============================================================"
	@echo "Main Components:"
	@echo "  - app.py: Application entry point"
	@echo "  - routes/: API endpoints and HTML pages"
	@echo "  - stores/: In-memory data storage"
	@echo "  - utils/: Helper functions"
	@echo "  - templates/: HTML templates"
	@echo "  - static/: Frontend assets (CSS, JS)"
	@echo "============================================================"
	@echo "Run 'make start' to start the application"
	@echo "Run 'make dev' to start in development mode"
	@echo "============================================================"