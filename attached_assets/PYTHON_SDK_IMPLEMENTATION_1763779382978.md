
# Arca Python SDK Implementation Guide

## Overview

This document provides complete implementation details for creating a Python SDK for Arca - a private data vault for personal AI assistants. The SDK will mirror the existing TypeScript SDK functionality and provide a clean, pythonic interface for interacting with Arca's Tables and Vectors APIs.

## Project Structure

Create a new repository with the following structure:

```
arca-python-sdk/
├── arca/
│   ├── __init__.py
│   ├── client.py
│   ├── models.py
│   ├── exceptions.py
│   └── version.py
├── examples/
│   ├── table_examples.py
│   ├── vector_examples.py
│   └── mcp_integration.py
├── tests/
│   ├── __init__.py
│   ├── test_table_client.py
│   └── test_vector_client.py
├── .gitignore
├── LICENSE
├── README.md
├── setup.py
├── pyproject.toml
└── requirements.txt
```

## Complete Implementation

### 1. `arca/__init__.py`

```python
"""
Arca Python SDK - Private data vault for personal AI assistants
"""

from .client import ArcaTableClient, ArcaVectorClient
from .models import (
    TableColumn,
    SkillMetadata,
    VectorSkillMetadata,
    MetadataField
)
from .exceptions import ArcaAPIError, ArcaAuthError, ArcaValidationError
from .version import __version__

__all__ = [
    'ArcaTableClient',
    'ArcaVectorClient',
    'TableColumn',
    'SkillMetadata',
    'VectorSkillMetadata',
    'MetadataField',
    'ArcaAPIError',
    'ArcaAuthError',
    'ArcaValidationError',
    '__version__'
]
```

### 2. `arca/version.py`

```python
__version__ = '0.1.0'
```

### 3. `arca/exceptions.py`

```python
"""
Custom exceptions for the Arca SDK
"""

class ArcaError(Exception):
    """Base exception for all Arca SDK errors"""
    pass


class ArcaAPIError(ArcaError):
    """Raised when the API returns an error response"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"API Error (status {status_code}): {message}" if status_code else message)


class ArcaAuthError(ArcaError):
    """Raised when authentication fails"""
    pass


class ArcaValidationError(ArcaError):
    """Raised when request validation fails"""
    pass
```

### 4. `arca/models.py`

```python
"""
Data models for the Arca SDK
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Literal


@dataclass
class TableColumn:
    """Represents a column in an Arca table"""
    name: str
    type: Literal['VARCHAR', 'INTEGER', 'BIGINT', 'DOUBLE', 'BOOLEAN', 'TIMESTAMP', 'DATE', 'JSON']
    nullable: Optional[bool] = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SkillMetadata:
    """Metadata for table skills - helps AI understand how to use the table"""
    description: Optional[str] = None
    examples: Optional[List[str]] = None
    relationships: Optional[List[str]] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MetadataField:
    """Metadata field definition for vector tables"""
    name: str
    type: str
    description: str
    examples: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class VectorSkillMetadata:
    """Metadata for vector skills - helps AI understand how to search the vector table"""
    description: Optional[str] = None
    metadata_fields: Optional[List[MetadataField]] = None
    search_examples: Optional[List[str]] = None
    filter_examples: Optional[List[str]] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests"""
        result = {}
        if self.description:
            result['description'] = self.description
        if self.metadata_fields:
            result['metadata_fields'] = [f.to_dict() for f in self.metadata_fields]
        if self.search_examples:
            result['search_examples'] = self.search_examples
        if self.filter_examples:
            result['filter_examples'] = self.filter_examples
        if self.notes:
            result['notes'] = self.notes
        return result
```

### 5. `arca/client.py`

```python
"""
Main client classes for interacting with Arca API
"""

import requests
from typing import Dict, List, Optional, Any, Union
from .models import TableColumn, SkillMetadata, VectorSkillMetadata, MetadataField
from .exceptions import ArcaAPIError, ArcaAuthError, ArcaValidationError


class ArcaTableClient:
    """Client for interacting with Arca Tables API"""
    
    def __init__(self, user_id: str, base_url: str = "https://arca.fyi"):
        """
        Initialize the Arca Table Client
        
        Args:
            user_id: Your Arca API key (WorkOS user ID)
            base_url: Base URL for Arca API (default: https://arca.fyi)
        """
        if not user_id:
            raise ArcaAuthError("user_id (API key) is required")
        
        self.user_id = user_id
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {user_id}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal method to make HTTP requests with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            
            if response.status_code == 401:
                raise ArcaAuthError("Invalid API key")
            
            if not response.ok:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', f'Request failed with status {response.status_code}')
                raise ArcaAPIError(error_message, response.status_code)
            
            return response.json()
        except requests.RequestException as e:
            raise ArcaAPIError(f"Network error: {str(e)}")
    
    def upsert(
        self,
        table_name: str,
        data: Dict[str, Any],
        columns: Optional[List[TableColumn]] = None,
        skill: Optional[SkillMetadata] = None
    ) -> Dict[str, Any]:
        """
        Create or append to a table. This is the recommended method.
        
        Args:
            table_name: Name of the table
            data: Dictionary of data to insert
            columns: List of TableColumn objects (only needed on first insert)
            skill: Optional SkillMetadata to help AI understand the table
        
        Returns:
            Dictionary with success status, message, tableName, s3Path, and recordId
        
        Example:
            client.upsert(
                table_name="meals",
                columns=[
                    TableColumn("food", "VARCHAR"),
                    TableColumn("calories", "INTEGER")
                ],
                data={"food": "Pizza", "calories": 800},
                skill=SkillMetadata(
                    description="Tracks daily meals",
                    examples=["SELECT * FROM meals WHERE calories > 500"]
                )
            )
        """
        payload = {
            "tableName": table_name,
            "data": data
        }
        
        if columns:
            payload["columns"] = [col.to_dict() for col in columns]
        if skill:
            payload["skill"] = skill.to_dict()
        
        return self._make_request("POST", "/api/v1/tables/upsert", json=payload)
    
    def query(
        self,
        table_name: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        select: Optional[List[str]] = None,
        group_by: Optional[str] = None,
        having: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query a table with filters and aggregations
        
        Args:
            table_name: Name of the table to query
            query: Raw SQL WHERE clause
            filters: Dictionary of filters (e.g., {"daysAgo": 7, "food": "Pizza"})
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column to order by (e.g., "created_at DESC")
            select: List of columns to select
            group_by: Column to group by
            having: HAVING clause for aggregations
        
        Returns:
            Dictionary with success status, data array, and metadata
        
        Example:
            results = client.query(
                table_name="meals",
                filters={"daysAgo": 7},
                limit=10,
                order_by="calories DESC"
            )
        """
        payload = {"tableName": table_name}
        
        if query:
            payload["query"] = query
        if filters:
            payload["filters"] = filters
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset
        if order_by:
            payload["orderBy"] = order_by
        if select:
            payload["select"] = select
        if group_by:
            payload["groupBy"] = group_by
        if having:
            payload["having"] = having
        
        return self._make_request("POST", "/api/v1/tables/query", json=payload)
    
    def update(
        self,
        table_name: str,
        updates: Dict[str, Any],
        where: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update rows in a table
        
        Args:
            table_name: Name of the table
            updates: Dictionary of column:value pairs to update
            where: Raw SQL WHERE clause
            filters: Dictionary of filters
        
        Returns:
            Dictionary with success status and rows affected
        """
        payload = {
            "tableName": table_name,
            "updates": updates
        }
        
        if where:
            payload["where"] = where
        if filters:
            payload["filters"] = filters
        
        return self._make_request("POST", "/api/v1/tables/update", json=payload)
    
    def delete(self, table_name: str) -> Dict[str, Any]:
        """
        Delete an entire table
        
        Args:
            table_name: Name of the table to delete
        
        Returns:
            Dictionary with success status and message
        """
        payload = {"tableName": table_name}
        return self._make_request("DELETE", "/api/v1/tables/delete", json=payload)
    
    def list_tables(self) -> Dict[str, Any]:
        """
        List all tables for the authenticated user
        
        Returns:
            Dictionary with tableCount, tables array with name, s3Path, and rowCount
        """
        return self._make_request("GET", "/api/v1/tables/list")
    
    def get_schemas(self) -> Dict[str, Any]:
        """
        Get schemas for all tables
        
        Returns:
            Dictionary with schemas array containing tableName, s3Path, and columns
        """
        return self._make_request("GET", "/api/v1/tables/schemas")
    
    def get_skill(self, table_name: str) -> Dict[str, Any]:
        """
        Get the SKILL.md file for a specific table
        
        Args:
            table_name: Name of the table
        
        Returns:
            Dictionary with success status, tableName, and skill content
        """
        return self._make_request("GET", f"/api/v1/tables/{table_name}/skill")
    
    def update_skill(
        self,
        table_name: str,
        skill: SkillMetadata
    ) -> Dict[str, Any]:
        """
        Update the SKILL.md file for a table
        
        Args:
            table_name: Name of the table
            skill: SkillMetadata object with updated information
        
        Returns:
            Dictionary with success status and message
        """
        payload = {"skill": skill.to_dict()}
        return self._make_request("POST", f"/api/v1/tables/{table_name}/skill", json=payload)
    
    def get_all_skills(self) -> Dict[str, Any]:
        """
        Get all table skills in one request (useful for MCP context)
        
        Returns:
            Dictionary with skills array containing tableName and skill content
        """
        return self._make_request("GET", "/api/v1/tables/skills")
    
    def export(self, table_name: str) -> bytes:
        """
        Export a table as Parquet file
        
        Args:
            table_name: Name of the table to export
        
        Returns:
            Parquet file as bytes
        """
        url = f"{self.base_url}/api/v1/tables/export?tableName={table_name}"
        response = requests.get(url, headers=self.headers)
        
        if not response.ok:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', 'Export failed')
            raise ArcaAPIError(error_message, response.status_code)
        
        return response.content


class ArcaVectorClient:
    """Client for interacting with Arca Vectors API (semantic search)"""
    
    def __init__(self, user_id: str, base_url: str = "https://arca.fyi"):
        """
        Initialize the Arca Vector Client
        
        Args:
            user_id: Your Arca API key (WorkOS user ID)
            base_url: Base URL for Arca API (default: https://arca.fyi)
        """
        if not user_id:
            raise ArcaAuthError("user_id (API key) is required")
        
        self.user_id = user_id
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {user_id}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal method to make HTTP requests with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            
            if response.status_code == 401:
                raise ArcaAuthError("Invalid API key")
            
            if not response.ok:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', f'Request failed with status {response.status_code}')
                raise ArcaAPIError(error_message, response.status_code)
            
            return response.json()
        except requests.RequestException as e:
            raise ArcaAPIError(f"Network error: {str(e)}")
    
    def add(
        self,
        table_name: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        generate_embedding: bool = True,
        embedding: Optional[List[float]] = None,
        skill: Optional[VectorSkillMetadata] = None
    ) -> Dict[str, Any]:
        """
        Add a vector entry with automatic embedding generation
        
        Args:
            table_name: Name of the vector table
            text: Text content to embed and store
            metadata: Optional metadata dictionary
            generate_embedding: Whether to auto-generate embedding (default: True)
            embedding: Pre-computed embedding vector (if generate_embedding=False)
            skill: Optional VectorSkillMetadata to help AI understand the table
        
        Returns:
            Dictionary with success status, tableName, s3Path, embeddingDimension
        
        Example:
            client.add(
                table_name="journal_entries",
                text="Today was productive. Finished the project.",
                metadata={
                    "category": "personal",
                    "mood": "positive",
                    "tags": "productivity"
                },
                skill=VectorSkillMetadata(
                    description="Personal journal entries",
                    metadata_fields=[
                        MetadataField("category", "string", "Type of entry", ["personal", "work"]),
                        MetadataField("mood", "string", "Emotional state", ["positive", "neutral"])
                    ],
                    search_examples=["Find productive days"],
                    filter_examples=["mood = 'positive'"]
                )
            )
        """
        payload = {
            "tableName": table_name,
            "text": text,
            "generateEmbedding": generate_embedding
        }
        
        if metadata:
            payload["metadata"] = metadata
        if embedding:
            payload["embedding"] = embedding
        if skill:
            payload["skill"] = skill.to_dict()
        
        return self._make_request("POST", "/api/v1/vectors/add", json=payload)
    
    def search(
        self,
        table_name: str,
        query: str,
        limit: int = 5,
        generate_embedding: bool = True,
        embedding: Optional[List[float]] = None,
        filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search vectors semantically
        
        Args:
            table_name: Name of the vector table to search
            query: Search query text
            limit: Maximum number of results (default: 5)
            generate_embedding: Whether to auto-generate query embedding (default: True)
            embedding: Pre-computed query embedding vector
            filter: SQL-like filter expression (e.g., "category = 'personal'")
        
        Returns:
            Dictionary with success, tableName, query, resultCount, and results array
        
        Example:
            results = client.search(
                table_name="journal_entries",
                query="days when I felt accomplished",
                limit=5,
                filter="category = 'personal'"
            )
        """
        payload = {
            "tableName": table_name,
            "query": query,
            "limit": limit,
            "generateEmbedding": generate_embedding
        }
        
        if embedding:
            payload["embedding"] = embedding
        if filter:
            payload["filter"] = filter
        
        return self._make_request("POST", "/api/v1/vectors/search", json=payload)
    
    def delete(self, table_name: str) -> Dict[str, Any]:
        """
        Delete an entire vector table
        
        Args:
            table_name: Name of the vector table to delete
        
        Returns:
            Dictionary with success status and message
        """
        payload = {"tableName": table_name}
        return self._make_request("DELETE", "/api/v1/vectors/delete", json=payload)
    
    def list_tables(self) -> Dict[str, Any]:
        """
        List all vector tables for the authenticated user
        
        Returns:
            Dictionary with userId, tableCount, and tables array
        """
        return self._make_request("GET", "/api/v1/vectors/list")
    
    def get_skill(self, table_name: str) -> Dict[str, Any]:
        """
        Get the SKILL.md file for a specific vector table
        
        Args:
            table_name: Name of the vector table
        
        Returns:
            Dictionary with success status, tableName, and skill content
        """
        return self._make_request("GET", f"/api/v1/vectors/{table_name}/skill")
    
    def update_skill(
        self,
        table_name: str,
        skill: VectorSkillMetadata
    ) -> Dict[str, Any]:
        """
        Update the SKILL.md file for a vector table
        
        Args:
            table_name: Name of the vector table
            skill: VectorSkillMetadata object with updated information
        
        Returns:
            Dictionary with success status and message
        """
        payload = {"skill": skill.to_dict()}
        return self._make_request("POST", f"/api/v1/vectors/{table_name}/skill", json=payload)
    
    def get_all_skills(self) -> Dict[str, Any]:
        """
        Get all vector skills in one request (useful for MCP context)
        
        Returns:
            Dictionary with skills array containing tableName and skill content
        """
        return self._make_request("GET", "/api/v1/vectors/skills")
    
    def export(self, table_name: str) -> bytes:
        """
        Export a vector table as CSV file
        
        Args:
            table_name: Name of the vector table to export
        
        Returns:
            CSV file as bytes
        """
        url = f"{self.base_url}/api/v1/vectors/export?tableName={table_name}"
        response = requests.get(url, headers=self.headers)
        
        if not response.ok:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', 'Export failed')
            raise ArcaAPIError(error_message, response.status_code)
        
        return response.content
```

### 6. `setup.py`

```python
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from version.py
version = {}
with open("arca/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="arca-sdk",
    version=version['__version__'],
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
        ],
    },
    python_requires=">=3.8",
    author="Arca Team",
    author_email="support@arca.fyi",
    description="Python SDK for Arca - Private data vault for personal AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arca-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/arca-python-sdk/issues",
        "Documentation": "https://arca.fyi/docs",
        "Source Code": "https://github.com/yourusername/arca-python-sdk",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai, data, vault, storage, semantic-search, vector-database, personal-ai",
)
```

### 7. `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "arca-sdk"
dynamic = ["version"]
description = "Python SDK for Arca - Private data vault for personal AI"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Arca Team", email = "support@arca.fyi"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "flake8>=6.1.0",
    "mypy>=1.5.0",
]

[project.urls]
Homepage = "https://arca.fyi"
Documentation = "https://arca.fyi/docs"
Repository = "https://github.com/yourusername/arca-python-sdk"
"Bug Tracker" = "https://github.com/yourusername/arca-python-sdk/issues"
```

### 8. `requirements.txt`

```
requests>=2.31.0
```

### 9. `examples/table_examples.py`

```python
"""
Examples of using the Arca Table Client
"""

from arca import ArcaTableClient, TableColumn, SkillMetadata

# Initialize client with your API key
client = ArcaTableClient(
    user_id="user_01K742WHQXDGP25w0NFX4CBGVP",  # Replace with your Arca API key
    base_url="https://arca.fyi"
)

# Example 1: Create a new table with skill metadata
print("Example 1: Creating a meals table...")
result = client.upsert(
    table_name="meals",
    columns=[
        TableColumn("food", "VARCHAR"),
        TableColumn("calories", "INTEGER"),
        TableColumn("meal_type", "VARCHAR")
    ],
    data={
        "food": "Grilled chicken salad",
        "calories": 450,
        "meal_type": "lunch"
    },
    skill=SkillMetadata(
        description="Tracks daily meal consumption for nutrition analysis",
        examples=[
            "SELECT * FROM meals WHERE calories > 500",
            "SELECT meal_type, AVG(calories) FROM meals GROUP BY meal_type",
            "SELECT * FROM meals WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
        ],
        relationships=["Related to daily_nutrition table"],
        notes="Track all meals with calorie information for health monitoring"
    )
)
print(f"Created table: {result}")

# Example 2: Append more data to existing table
print("\nExample 2: Adding more meals...")
result = client.upsert(
    table_name="meals",
    data={
        "food": "Pizza",
        "calories": 800,
        "meal_type": "dinner"
    }
)
print(f"Added meal: {result}")

# Example 3: Query with filters
print("\nExample 3: Querying meals from last 7 days...")
results = client.query(
    table_name="meals",
    filters={"daysAgo": 7},
    limit=10,
    order_by="created_at DESC"
)
print(f"Found {len(results.get('data', []))} meals")
for meal in results.get('data', []):
    print(f"  - {meal['food']}: {meal['calories']} calories")

# Example 4: Query with custom WHERE clause
print("\nExample 4: Finding high-calorie meals...")
results = client.query(
    table_name="meals",
    query="calories > 600",
    order_by="calories DESC"
)
print(f"High-calorie meals: {results.get('data', [])}")

# Example 5: Aggregate queries
print("\nExample 5: Average calories by meal type...")
results = client.query(
    table_name="meals",
    select=["meal_type", "AVG(calories) as avg_calories"],
    group_by="meal_type"
)
print(f"Averages: {results.get('data', [])}")

# Example 6: Update rows
print("\nExample 6: Updating a meal...")
result = client.update(
    table_name="meals",
    updates={"calories": 750},
    where="food = 'Pizza'"
)
print(f"Updated: {result}")

# Example 7: List all tables
print("\nExample 7: Listing all tables...")
tables = client.list_tables()
print(f"Total tables: {tables.get('tableCount', 0)}")
for table in tables.get('tables', []):
    print(f"  - {table['name']}: {table.get('rowCount', 0)} rows")

# Example 8: Get table schemas
print("\nExample 8: Getting table schemas...")
schemas = client.get_schemas()
for schema in schemas.get('schemas', []):
    print(f"\nTable: {schema['tableName']}")
    for col in schema['columns']:
        print(f"  - {col['name']}: {col['type']}")

# Example 9: Get and update skill
print("\nExample 9: Managing skills...")
skill = client.get_skill("meals")
print(f"Current skill: {skill.get('skill', '')[:100]}...")

# Update skill
client.update_skill(
    "meals",
    SkillMetadata(
        description="Updated: Comprehensive meal tracking system",
        examples=["SELECT * FROM meals WHERE calories BETWEEN 400 AND 600"]
    )
)

# Example 10: Export table
print("\nExample 10: Exporting table...")
parquet_data = client.export("meals")
with open("meals_export.parquet", "wb") as f:
    f.write(parquet_data)
print("Exported to meals_export.parquet")
```

### 10. `examples/vector_examples.py`

```python
"""
Examples of using the Arca Vector Client
"""

from arca import ArcaVectorClient, VectorSkillMetadata, MetadataField

# Initialize client with your API key
client = ArcaVectorClient(
    user_id="user_01K742WHQXDGP25w0NFX4CBGVP",  # Replace with your Arca API key
    base_url="https://arca.fyi"
)

# Example 1: Add journal entries with skill metadata
print("Example 1: Adding journal entries...")
result = client.add(
    table_name="journal_entries",
    text="Today was incredibly productive. I finished the project proposal, went for a 5k run, and had a great dinner with friends.",
    metadata={
        "category": "personal",
        "mood": "positive",
        "tags": "productivity, exercise, social"
    },
    skill=VectorSkillMetadata(
        description="Personal journal entries tracking daily activities and reflections",
        metadata_fields=[
            MetadataField(
                name="category",
                type="string",
                description="Type of entry",
                examples=["personal", "work", "health", "social"]
            ),
            MetadataField(
                name="mood",
                type="string",
                description="Emotional state during entry",
                examples=["positive", "neutral", "negative", "mixed"]
            ),
            MetadataField(
                name="tags",
                type="string",
                description="Comma-separated tags for categorization",
                examples=["productivity, exercise", "relaxation, mindfulness"]
            )
        ],
        search_examples=[
            "Find productive days",
            "Show entries about exercise",
            "Days when I felt happy",
            "Work accomplishments"
        ],
        filter_examples=[
            "mood = 'positive'",
            "category = 'work'",
            "tags LIKE '%exercise%'"
        ],
        notes="Journal entries are private and searchable by semantic meaning. Great for reflection and tracking personal growth."
    )
)
print(f"Added entry: {result}")

# Example 2: Add more journal entries
print("\nExample 2: Adding more entries...")
entries = [
    {
        "text": "Struggled with focus today. Had too many meetings and couldn't get into deep work.",
        "metadata": {"category": "work", "mood": "frustrated", "tags": "productivity, meetings"}
    },
    {
        "text": "Morning meditation was peaceful. Feeling centered and calm.",
        "metadata": {"category": "health", "mood": "positive", "tags": "mindfulness, meditation"}
    },
    {
        "text": "Great coding session! Solved that tricky bug and learned about async patterns.",
        "metadata": {"category": "work", "mood": "positive", "tags": "coding, learning"}
    }
]

for entry in entries:
    client.add(
        table_name="journal_entries",
        text=entry["text"],
        metadata=entry["metadata"]
    )
print("Added multiple entries")

# Example 3: Semantic search
print("\nExample 3: Searching for productive days...")
results = client.search(
    table_name="journal_entries",
    query="days when I felt accomplished and got things done",
    limit=5
)
print(f"Found {results.get('resultCount', 0)} results:")
for result in results.get('results', []):
    print(f"\n  Distance: {result.get('_distance', 0):.4f}")
    print(f"  Text: {result['text']}")
    print(f"  Metadata: {result}")

# Example 4: Search with filters
print("\nExample 4: Searching work-related entries...")
results = client.search(
    table_name="journal_entries",
    query="challenging or difficult situations",
    limit=3,
    filter="category = 'work'"
)
print(f"Work challenges: {results.get('resultCount', 0)} results")

# Example 5: Add recipes
print("\nExample 5: Creating a recipes collection...")
client.add(
    table_name="recipes",
    text="Grandma's chocolate chip cookies - soft, chewy, with a hint of vanilla. Uses brown sugar for extra moisture.",
    metadata={
        "category": "dessert",
        "difficulty": "easy",
        "tags": "baking, cookies, family",
        "prep_time": "15 min",
        "cook_time": "12 min"
    }
)

client.add(
    table_name="recipes",
    text="Quick weeknight stir-fry with chicken, bell peppers, and teriyaki sauce. Ready in 20 minutes!",
    metadata={
        "category": "dinner",
        "difficulty": "easy",
        "tags": "quick, healthy, asian",
        "prep_time": "10 min",
        "cook_time": "10 min"
    }
)

# Example 6: Search recipes
print("\nExample 6: Finding quick dinner recipes...")
results = client.search(
    table_name="recipes",
    query="fast and easy dinner options",
    filter="difficulty = 'easy'"
)
print(f"Quick recipes: {results.get('resultCount', 0)} results")
for recipe in results.get('results', []):
    print(f"  - {recipe['text'][:60]}...")

# Example 7: List all vector tables
print("\nExample 7: Listing all vector tables...")
tables = client.list_tables()
print(f"Total vector tables: {tables.get('tableCount', 0)}")
for table in tables.get('tables', []):
    print(f"  - {table['name']}")

# Example 8: Get all skills (for MCP context)
print("\nExample 8: Getting all skills...")
all_skills = client.get_all_skills()
for skill in all_skills.get('skills', []):
    print(f"\nTable: {skill['tableName']}")
    print(f"Skill preview: {skill.get('skill', '')[:100]}...")

# Example 9: Export vector table
print("\nExample 9: Exporting journal entries...")
csv_data = client.export("journal_entries")
with open("journal_export.csv", "wb") as f:
    f.write(csv_data)
print("Exported to journal_export.csv")
```

### 11. `examples/mcp_integration.py`

```python
"""
Example of using Arca SDK with Model Context Protocol (MCP) servers
"""

import os
from arca import ArcaTableClient, ArcaVectorClient

# This example shows how to integrate Arca with MCP servers
# MCP is a protocol for AI assistants to interact with external tools

class ArcaMCPTools:
    """MCP tools wrapper for Arca"""
    
    def __init__(self, user_id: str = None):
        # Get user ID from environment or parameter
        self.user_id = user_id or os.getenv("ARCA_USER_ID")
        if not self.user_id:
            raise ValueError("ARCA_USER_ID must be set in environment or passed as parameter")
        
        self.table_client = ArcaTableClient(self.user_id)
        self.vector_client = ArcaVectorClient(self.user_id)
    
    async def save_memory(self, content: str, category: str = "general") -> dict:
        """
        MCP Tool: Save a memory to Arca
        
        Usage in MCP server:
            @app.call_tool()
            async def save_memory(content: str, category: str = "general"):
                tools = ArcaMCPTools()
                return tools.save_memory(content, category)
        """
        result = self.vector_client.add(
            table_name="memories",
            text=content,
            metadata={"category": category}
        )
        return {
            "success": result.get("success", False),
            "message": f"Saved memory to {result.get('tableName')}"
        }
    
    async def search_memories(self, query: str, category: str = None, limit: int = 5) -> dict:
        """
        MCP Tool: Search memories semantically
        
        Usage in MCP server:
            @app.call_tool()
            async def search_memories(query: str, category: str = None, limit: int = 5):
                tools = ArcaMCPTools()
                return tools.search_memories(query, category, limit)
        """
        filter_clause = f"category = '{category}'" if category else None
        
        results = self.vector_client.search(
            table_name="memories",
            query=query,
            limit=limit,
            filter=filter_clause
        )
        
        return {
            "count": results.get("resultCount", 0),
            "memories": [
                {
                    "text": r["text"],
                    "category": r.get("category"),
                    "relevance": 1 - r.get("_distance", 0)
                }
                for r in results.get("results", [])
            ]
        }
    
    async def track_data(self, table_name: str, data: dict) -> dict:
        """
        MCP Tool: Track structured data
        
        Usage in MCP server:
            @app.call_tool()
            async def track_data(table_name: str, data: dict):
                tools = ArcaMCPTools()
                return tools.track_data(table_name, data)
        """
        result = self.table_client.upsert(
            table_name=table_name,
            data=data
        )
        return {
            "success": result.get("success", False),
            "message": f"Tracked data in {table_name}",
            "record_id": result.get("recordId")
        }
    
    async def query_data(self, table_name: str, filters: dict = None, limit: int = 10) -> dict:
        """
        MCP Tool: Query structured data
        
        Usage in MCP server:
            @app.call_tool()
            async def query_data(table_name: str, filters: dict = None, limit: int = 10):
                tools = ArcaMCPTools()
                return tools.query_data(table_name, filters, limit)
        """
        results = self.table_client.query(
            table_name=table_name,
            filters=filters,
            limit=limit
        )
        return {
            "success": results.get("success", False),
            "data": results.get("data", []),
            "count": len(results.get("data", []))
        }
    
    async def get_context(self) -> dict:
        """
        MCP Tool: Get all skills for context (what data the user has)
        
        This is useful for providing context to the AI about available data
        
        Usage in MCP server:
            @app.list_resources()
            async def list_resources():
                tools = ArcaMCPTools()
                context = tools.get_context()
                return context
        """
        table_skills = self.table_client.get_all_skills()
        vector_skills = self.vector_client.get_all_skills()
        
        return {
            "tables": [
                {
                    "name": skill["tableName"],
                    "type": "structured",
                    "description": skill.get("skill", "")[:200]
                }
                for skill in table_skills.get("skills", [])
            ],
            "vectors": [
                {
                    "name": skill["tableName"],
                    "type": "semantic",
                    "description": skill.get("skill", "")[:200]
                }
                for skill in vector_skills.get("skills", [])
            ]
        }


# Example MCP Server Implementation (using mcp library)
"""
from mcp.server import Server
import os

app = Server("arca-mcp")
tools = ArcaMCPTools(os.getenv("ARCA_USER_ID"))

@app.call_tool()
async def save_memory(content: str, category: str = "general"):
    return await tools.save_memory(content, category)

@app.call_tool()
async def search_memories(query: str, category: str = None, limit: int = 5):
    return await tools.search_memories(query, category, limit)

@app.call_tool()
async def track_data(table_name: str, data: dict):
    return await tools.track_data(table_name, data)

@app.call_tool()
async def query_data(table_name: str, filters: dict = None, limit: int = 10):
    return await tools.query_data(table_name, filters, limit)

@app.list_resources()
async def list_resources():
    return await tools.get_context()

if __name__ == "__main__":
    app.run()
"""
```

### 12. `tests/test_table_client.py`

```python
"""
Tests for ArcaTableClient
"""

import pytest
from unittest.mock import Mock, patch
from arca import ArcaTableClient, TableColumn, SkillMetadata
from arca.exceptions import ArcaAuthError, ArcaAPIError


@pytest.fixture
def client():
    return ArcaTableClient(user_id="test_user_123", base_url="https://test.arca.fyi")


def test_client_initialization():
    client = ArcaTableClient("test_user")
    assert client.user_id == "test_user"
    assert client.base_url == "https://arca.fyi"


def test_client_no_user_id():
    with pytest.raises(ArcaAuthError):
        ArcaTableClient("")


@patch('requests.request')
def test_upsert_success(mock_request, client):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "success": True,
        "tableName": "test_table",
        "recordId": 1
    }
    mock_request.return_value = mock_response
    
    result = client.upsert(
        table_name="test_table",
        data={"name": "test"}
    )
    
    assert result["success"] is True
    assert result["tableName"] == "test_table"


@patch('requests.request')
def test_upsert_with_columns_and_skill(mock_request, client):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response
    
    columns = [TableColumn("name", "VARCHAR")]
    skill = SkillMetadata(description="Test table")
    
    client.upsert(
        table_name="test_table",
        columns=columns,
        data={"name": "test"},
        skill=skill
    )
    
    call_args = mock_request.call_args
    payload = call_args.kwargs['json']
    
    assert 'columns' in payload
    assert 'skill' in payload
    assert payload['columns'][0]['name'] == 'name'


@patch('requests.request')
def test_query_success(mock_request, client):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "success": True,
        "data": [{"id": 1, "name": "test"}]
    }
    mock_request.return_value = mock_response
    
    result = client.query(
        table_name="test_table",
        filters={"daysAgo": 7},
        limit=10
    )
    
    assert result["success"] is True
    assert len(result["data"]) == 1


@patch('requests.request')
def test_api_error(mock_request, client):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad request"}
    mock_request.return_value = mock_response
    
    with pytest.raises(ArcaAPIError) as exc_info:
        client.upsert(table_name="test", data={})
    
    assert "Bad request" in str(exc_info.value)


@patch('requests.request')
def test_auth_error(mock_request, client):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_request.return_value = mock_response
    
    with pytest.raises(ArcaAuthError):
        client.list_tables()
```

### 13. `README.md`

```markdown
# Arca Python SDK

Python SDK for [Arca](https://arca.fyi) - A private data vault for personal AI assistants.

## Installation

```bash
pip install arca-sdk
```

## Quick Start

### Tables (Structured Data)

```python
from arca import ArcaTableClient, TableColumn, SkillMetadata

# Initialize client
client = ArcaTableClient(
    user_id="your_arca_api_key",
    base_url="https://arca.fyi"
)

# Create/update table with skill metadata
client.upsert(
    table_name="meals",
    columns=[
        TableColumn("food", "VARCHAR"),
        TableColumn("calories", "INTEGER")
    ],
    data={"food": "Pizza", "calories": 800},
    skill=SkillMetadata(
        description="Tracks daily meals for nutrition",
        examples=["SELECT * FROM meals WHERE calories > 500"]
    )
)

# Query data
results = client.query(
    table_name="meals",
    filters={"daysAgo": 7},
    limit=10
)
```

### Vectors (Semantic Search)

```python
from arca import ArcaVectorClient, VectorSkillMetadata, MetadataField

# Initialize client
client = ArcaVectorClient(
    user_id="your_arca_api_key",
    base_url="https://arca.fyi"
)

# Add entries with automatic embedding
client.add(
    table_name="memories",
    text="Had brunch at Cafe Luna with Sarah",
    metadata={
        "category": "experience",
        "location": "Cafe Luna"
    },
    skill=VectorSkillMetadata(
        description="Personal memories and experiences",
        metadata_fields=[
            MetadataField("category", "string", "Type of memory"),
            MetadataField("location", "string", "Where it happened")
        ]
    )
)

# Search semantically
results = client.search(
    table_name="memories",
    query="great restaurant experiences",
    limit=5
)
```

## Features

- **Structured Tables**: Store and query structured data with DuckDB
- **Semantic Vectors**: Automatic embedding generation for semantic search
- **Skills System**: AI-readable metadata for better context
- **Type Safety**: Full type hints for better IDE support
- **Error Handling**: Comprehensive exception handling
- **MCP Integration**: Easy integration with Model Context Protocol servers

## Documentation

- [API Reference](https://arca.fyi/docs)
- [Examples](./examples/)
- [MCP Integration Guide](./examples/mcp_integration.py)

## Requirements

- Python 3.8+
- requests >= 2.31.0

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/arca-python-sdk
cd arca-python-sdk

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black arca/ tests/ examples/

# Type checking
mypy arca/
```

## License

MIT License - see LICENSE file for details

## Support

- Email: support@arca.fyi
- Documentation: https://arca.fyi/docs
- Issues: https://github.com/yourusername/arca-python-sdk/issues
```

### 14. `.gitignore`

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.parquet
*.csv
*.db
.env
.env.local
```

## Publishing to PyPI

Once implemented, publish with:

```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Testing the SDK

```bash
# Install locally for testing
pip install -e .

# Run examples
python examples/table_examples.py
python examples/vector_examples.py
```

## Next Steps

1. Create GitHub repository
2. Implement all files as shown above
3. Add comprehensive tests
4. Set up CI/CD (GitHub Actions)
5. Publish to PyPI
6. Create documentation site
7. Add more examples for common use cases

## Notes

- The SDK mirrors the TypeScript implementation exactly
- All API endpoints from the Arca API are supported
- Error handling is comprehensive with custom exceptions
- Type hints are used throughout for better IDE support
- Suitable for both standalone use and MCP server integration
```
