# ClashBot Go Makefile

.PHONY: build run test clean lint format install-deps

# Binary name
BINARY_NAME=clashbot
BINARY_PATH=./cmd/bot

# Build the application
build:
	@echo "Building $(BINARY_NAME) for current platform..."
	go build -o $(BINARY_NAME) $(BINARY_PATH)

# Build for Linux (production)
build-linux:
	@echo "Building $(BINARY_NAME) for Linux..."
	GOOS=linux GOARCH=amd64 go build -o $(BINARY_NAME)-linux $(BINARY_PATH)

# Run the application
run:
	@echo "Running $(BINARY_NAME)..."
	go run $(BINARY_PATH)

# Run with config file
run-config:
	@echo "Running $(BINARY_NAME) with custom config..."
	CONFIG_PATH=./configs/config.yaml go run $(BINARY_PATH)

# Run tests
test:
	@echo "Running tests..."
	go test -v ./...

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BINARY_NAME) $(BINARY_NAME)-linux
	rm -f coverage.out coverage.html
	go clean

# Lint code
lint:
	@echo "Running linter..."
	golangci-lint run

# Format code
format:
	@echo "Formatting code..."
	go fmt ./...
	goimports -w .

# Install dependencies
install-deps:
	@echo "Installing dependencies..."
	go mod download
	go mod tidy

# Install development tools
install-tools:
	@echo "Installing development tools..."
	go install golang.org/x/tools/cmd/goimports@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t clashbot:latest .

# Docker run
docker-run:
	@echo "Running Docker container..."
	docker run --rm -it clashbot:latest

# Show help
help:
	@echo "Available commands:"
	@echo "  build          - Build the application"
	@echo "  build-linux    - Build for Linux"
	@echo "  run            - Run the application"
	@echo "  run-config     - Run with custom config"
	@echo "  test           - Run tests"
	@echo "  test-coverage  - Run tests with coverage"
	@echo "  clean          - Clean build artifacts"
	@echo "  lint           - Run linter"
	@echo "  format         - Format code"
	@echo "  install-deps   - Install dependencies"
	@echo "  install-tools  - Install development tools"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"