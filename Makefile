.PHONY: help build install dev clean test list get api start claude

help:
	@echo "SQL to Snowflake MCP Server"
	@echo ""
	@echo "Core Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build and discover resources"
	@echo "  make list       - List all resources"
	@echo ""
	@echo "API & ChatGPT Commands:"
	@echo "  make api        - Start REST API server (port 5000)"
	@echo "  make api-port   - Start API on custom port (make api-port PORT=8000)"
	@echo "  make start      - Quick start with auto-build"
	@echo ""
	@echo "Claude Integration:"
	@echo "  make claude     - Start interactive Claude chat"
	@echo "  make claude-q   - Ask Claude a question (make claude-q Q='Your question')"
	@echo "  make claude-v   - Claude chat with verbose output"
	@echo ""
	@echo "Development:"
	@echo "  make dev        - Run in development mode"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run tests"

install:
	pip install -r requirements.txt

build:
	python build.py

list:
	python mcp_server.py list

get:
	@echo "Usage: make get RESOURCE=resource_id"
	python mcp_server.py get $(RESOURCE)

category:
	@echo "Usage: make category CATEGORY=schema"
	python mcp_server.py category $(CATEGORY)

api:
	python api_server.py 5000

api-port:
	@echo "Usage: make api-port PORT=8000"
	python api_server.py $(PORT)

claude:
	python claude_client.py

claude-q:
	@echo "Usage: make claude-q Q='Your question'"
	python claude_client.py -q "$(Q)"

claude-v:
	python claude_client.py -v

start: build
	bash start.sh

dev: build
	python mcp_server.py list

clean:
	rm -rf dist/
	rm -f mcp-resources.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test:
	python -m pytest tests/ -v

.DEFAULT_GOAL := help
