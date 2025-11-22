# Arca Python SDK

## Overview

The Arca Python SDK is a client library for interacting with Arca's data vault APIs. Arca provides two primary APIs for storing and retrieving data:

1. **Tables API**: SQL-like structured data storage powered by DuckDB and Parquet
2. **Vectors API**: Semantic search over unstructured data using vector embeddings

The SDK is designed to be a Python equivalent of the TypeScript SDK, providing developers with a Pythonic interface to store personal AI assistant data privately and securely.

## Recent Changes

### November 22, 2025 - Fixed Query and Update API Calls

**Issue 1 - Query Filter Comparison Operators**: 
SDK clients were unable to use comparison operators (`>`, `<`, `>=`, `<=`, etc.) in queries because the SDK was sending the `query` parameter incorrectly.

**Fix**: Updated `ArcaTableClient.query()` to map the `query` parameter to `filters.customWhere` to match the server API.

**Issue 2 - Update Method Parameter Mismatch**:
The SDK's `update()` method was using incorrect parameter names (`updates` and `filters`) instead of what the server expects (`data` and `where`).

**Fix Applied**:
- Changed `updates` parameter to `data` to match server API
- Changed `where` parameter from string (SQL clause) to dict (exact matches like `{"id": 5}`)
- Updated all examples and documentation
- Removed `filters` parameter (not supported by update endpoint)

**Impact**: 
```python
# Query with comparison operators now works
client.query(table_name="meals", query="calories > 500")

# Update now matches server API format
client.update(
    table_name="meals",
    data={"calories": 910, "meal_type": "dinner"},
    where={"id": 5}
)
```

**Breaking Change**: The `update()` method signature changed. Users need to:
- Rename `updates=` to `data=`
- Change `where=` from string to dict format

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Client Architecture

**Two-Client Design Pattern**
- The SDK separates concerns into two distinct clients: `ArcaTableClient` for structured data and `ArcaVectorClient` for vector/embedding operations
- Both clients share common patterns for authentication, error handling, and HTTP communication
- Rationale: This separation mirrors the API structure and makes it clear which operations are available for each data type
- Alternative considered: Single unified client with method prefixes (e.g., `table_upsert`, `vector_add`), but rejected for clarity

**Authentication Mechanism**
- Uses bearer token authentication with WorkOS user IDs as API keys
- API key passed via `user_id` parameter during client initialization
- Tokens included in `Authorization` header for all requests
- Rationale: Matches existing API authentication patterns and provides consistent security model

**Base URL Configuration**
- Default base URL: `https://arca.build`
- Configurable via constructor parameter for testing/development environments
- Rationale: Production-first defaults with flexibility for testing

### Data Models

**Type-Safe Data Structures**
- Uses Python `dataclasses` for structured data representation
- Models include: `TableColumn`, `SkillMetadata`, `VectorSkillMetadata`, `MetadataField`
- Each model provides `to_dict()` method for API serialization
- Rationale: Dataclasses provide type safety, auto-generated methods, and clean serialization without external dependencies

**Column Type System**
- Supports SQL-like types: VARCHAR, INTEGER, BIGINT, DOUBLE, BOOLEAN, TIMESTAMP, DATE, JSON
- Enforced via `Literal` type hints for compile-time validation
- Rationale: Matches backend DuckDB capabilities while providing Python-native type checking

**Skill Metadata Pattern**
- Both table and vector APIs use metadata to help AI understand data structure
- Includes description, examples, relationships, and usage notes
- Rationale: Essential for AI assistants to autonomously use stored data correctly

### Error Handling

**Exception Hierarchy**
- Base `ArcaError` class for all SDK exceptions
- Specialized exceptions: `ArcaAPIError`, `ArcaAuthError`, `ArcaValidationError`
- API errors include status codes when available
- Rationale: Allows granular error handling and provides context for debugging

**Network Error Handling**
- Wraps `requests.RequestException` in `ArcaAPIError`
- Provides consistent error interface regardless of failure source
- Rationale: Shields users from underlying HTTP library details

### API Request Pattern

**Centralized Request Handler**
- `_make_request()` method handles all HTTP communication
- Manages headers, error checking, and response parsing in one place
- Automatically converts 401s to `ArcaAuthError`
- Rationale: DRY principle and consistent error handling across all endpoints

**Request/Response Format**
- All requests use JSON content type
- Responses parsed as JSON dictionaries
- Rationale: Matches REST API conventions and Python's native dict handling

### Package Structure

**Modular Organization**
- `client.py`: Client implementations
- `models.py`: Data structures
- `exceptions.py`: Error classes
- `version.py`: Version string (single source of truth)
- Rationale: Logical separation of concerns, easy navigation

**Public API Surface**
- All public classes exported via `__init__.py`
- Uses `__all__` to explicitly declare public interface
- Rationale: Clear contract for SDK users, enables `from arca import *` safely

## External Dependencies

### HTTP Client
- **Library**: `requests` (>=2.31.0)
- **Purpose**: HTTP communication with Arca API
- **Rationale**: Industry-standard, stable, widely-understood library with excellent documentation
- **Alternative considered**: `httpx` for async support, but synchronous operations sufficient for current use case

### Arca API Backend
- **Endpoint**: https://arca.build
- **Authentication**: Bearer token (WorkOS user IDs)
- **Tables API**: DuckDB-backed SQL-like operations on Parquet files
- **Vectors API**: Embedding generation and semantic search
- **Rate limiting**: Not currently specified in SDK

### Development Dependencies (extras)
- **pytest**: Testing framework
- **pytest-cov**: Code coverage reporting
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Static type checking
- **Purpose**: Development workflow tools for maintaining code quality

### Distribution
- **PyPI**: Package published as `arca-sdk`
- **Packaging**: Uses setuptools with setup.py
- **Python Version**: Requires Python 3.8+
- **Rationale**: setup.py provides compatibility with older build tools while supporting modern Python versions