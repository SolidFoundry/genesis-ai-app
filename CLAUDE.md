# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Project Setup and Running
- `make setup` - Set up development environment using Poetry
- `make run` - Start development server with hot reload
- `make run-prod` - Start production server with 4 workers
- `python run.py --auto-init` - Auto-initialize database and start app
- `start.bat` - Windows batch script to start the application

### MCP Server Management
- `scripts/mcp_start.bat` / `scripts/mcp_start.sh` - Start MCP server
- `scripts/mcp_stop.bat` / `scripts/mcp_stop.sh` - Stop MCP server
- `python -m apps.mcp_server.main` - Run MCP server directly

### Database Operations
- `make db-migrate` - Run database migrations using Alembic
- `make db-downgrade` - Rollback database migration
- `make db-revision` - Create new database migration
- `python run.py --init-db` - Initialize database structure
- `python run.py --init-sample` - Initialize sample data

### Testing
- `make test` - Run all tests
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests only
- `make test-e2e` - Run end-to-end tests only
- `make test-coverage` - Run tests with coverage report

### Code Quality
- `make lint` - Run code quality checks (ruff + mypy)
- `make format` - Format code (black + ruff fix)
- `make format-check` - Check code formatting
- `make security` - Run security checks with bandit

### Dependency Management
- `make install` - Install dependencies
- `make install-dev` - Install development dependencies
- `make update` - Update dependencies
- `make lock` - Generate dependency lock file

### Docker and Deployment
- `docker-compose up -d` - Start all services (app + database)
- `docker-compose down` - Stop all services
- `make build` - Build project
- `make clean` - Clean temporary files

## Architecture Overview

This is an enterprise-grade AI application starter kit built with FastAPI and clean architecture principles.

### Core Architecture
- **Layered Architecture**: Enforced through import-linter with layers: apps → genesis.business_logic → genesis.infrastructure
- **Dependency Injection**: Uses `dependency-injector` for IoC container
- **Domain-Driven Design**: Clear separation between business logic and infrastructure

### Key Components

#### Application Layer (`apps/`)
- `apps/rest_api/main.py` - FastAPI application entry point
- `apps/rest_api/v1/routers/` - API route definitions
- Handles HTTP requests, responses, and API documentation

#### Business Logic Layer (`src/genesis/`)
- `src/genesis/core/` - Core application services and utilities
- `src/genesis/ai_tools/` - AI tool integration and registry
- `src/genesis/business_logic/` - Business rules and domain logic

#### Infrastructure Layer (`src/genesis/infrastructure/`)
- `src/genesis/infrastructure/database/` - Database management with SQLAlchemy
- `src/genesis/infrastructure/llm/` - LLM provider integrations (OpenAI, Qwen)
- `src/genesis/infrastructure/` - External service integrations

### Database Architecture
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic for database schema management
- **Connection Pooling**: Configurable pool settings
- **Models**: Defined in `src/genesis/infrastructure/database/models.py`

### LLM Integration
- **Multi-Provider Support**: OpenAI and Qwen providers
- **Service Abstraction**: Common interface for different LLM providers
- **Configuration**: Environment-based provider configuration
- **Session Management**: Memory-based session storage for conversations

### AI Tools System
- **Plugin Architecture**: Extensible AI tools system
- **Registry Pattern**: Dynamic tool registration
- **Tool Interface**: Standardized tool execution interface
- **Math Tools**: Example implementation of mathematical tools

### Configuration Management
- **Environment-based**: Uses `.env` files for configuration
- **Pydantic Settings**: Type-safe configuration with `pydantic-settings`
- **Multi-environment**: Development and production configurations
- **Database Settings**: Separate database configuration section

### Logging and Monitoring
- **Structured Logging**: Uses `structlog` for structured logging
- **Request Tracing**: Request ID middleware for distributed tracing
- **Performance Monitoring**: Timing middleware for performance metrics
- **Health Checks**: Built-in health check endpoints

## Development Workflow

### Setting Up Development Environment
1. Install Poetry dependency manager
2. Run `make setup` to install dependencies
3. Configure `.env` file with database and API credentials
4. Run `python run.py --auto-init` to initialize database and start app

### Database Setup
- Use Docker Compose for PostgreSQL: `docker-compose up -d`
- Run migrations: `make db-migrate`
- Initialize sample data: `python run.py --init-sample`

### Testing Strategy
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`
- Coverage reporting with `make test-coverage`

### Code Quality Standards
- **Formatting**: Black code formatter with 88 character line length
- **Linting**: Ruff for fast linting with specific rule sets
- **Type Checking**: MyPy with strict mode enabled
- **Import Linting**: Enforces layered architecture through import-linter

## Important Configuration Files

- `pyproject.toml` - Poetry configuration, dependencies, and tool settings
- `docker-compose.yml` - Docker services configuration
- `logging_config.yaml` - Structured logging configuration
- `.env.example` - Environment variables template
- `Makefile` - Common development commands
- `run.py` - Application entry point with initialization options

## Environment Variables

Key environment variables that need to be configured:
- `DATABASE_*` - Database connection and pool settings
- `LLM_*` / `OPENAI_*` - LLM provider API keys and settings
- `APP_ENV` - Application environment (development/production)
- `DEBUG` - Debug mode flag

## Key Endpoints

- `/health` - Application health check
- `/docs` - Swagger API documentation
- `/api/v1/llm-with-tools` - LLM integration with tools
- `/v1/_debug/` - Debug endpoints for development