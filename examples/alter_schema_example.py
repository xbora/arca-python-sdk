
"""
Example demonstrating how to alter table schemas using the Arca SDK
"""

from arca import ArcaTableClient, TableColumn


def alter_schema_examples(api_key: str):
    """Demonstrate schema alteration operations"""
    client = ArcaTableClient(user_id=api_key)
    
    # Example 1: Add a single column with a default value
    print("1. Adding a 'category' column to meals table...")
    result = client.alter_schema(
        table_name="meals",
        add_columns=[
            TableColumn("category", "VARCHAR")
        ],
        default_values={
            "category": "General"
        }
    )
    print(f"Result: {result}")
    print(f"Columns added: {result.get('changes', {}).get('columnsAdded', [])}")
    
    # Example 2: Add multiple columns at once
    print("\n2. Adding multiple columns to meals table...")
    result = client.alter_schema(
        table_name="meals",
        add_columns=[
            TableColumn("priority", "INTEGER"),
            TableColumn("status", "VARCHAR"),
            TableColumn("notes", "VARCHAR")
        ],
        default_values={
            "priority": 0,
            "status": "pending",
            "notes": None
        }
    )
    print(f"Result: {result}")
    print(f"New schema: {result.get('newSchema', [])}")
    
    # Example 3: Add a boolean column
    print("\n3. Adding a boolean 'is_favorite' column...")
    result = client.alter_schema(
        table_name="meals",
        add_columns=[
            TableColumn("is_favorite", "BOOLEAN")
        ],
        default_values={
            "is_favorite": False
        }
    )
    print(f"Result: {result}")
    
    # Example 4: Add timestamp column
    print("\n4. Adding timestamp columns for tracking...")
    result = client.alter_schema(
        table_name="meals",
        add_columns=[
            TableColumn("last_modified", "TIMESTAMP"),
            TableColumn("review_date", "DATE")
        ],
        default_values={
            "last_modified": None,
            "review_date": None
        }
    )
    print(f"Result: {result}")
    
    # Verify the changes by querying the schema
    print("\n5. Verifying schema changes...")
    schemas = client.get_schemas()
    for schema in schemas.get('schemas', []):
        if schema['tableName'] == 'meals':
            print(f"\nFinal schema for 'meals' table:")
            for column in schema.get('columns', []):
                print(f"  - {column['name']}: {column['type']}")


if __name__ == "__main__":
    # Replace with your actual API key from https://arca.build
    API_KEY = "your-api-key-here"
    
    print("=== Arca Alter Schema Examples ===\n")
    
    try:
        alter_schema_examples(API_KEY)
        print("\n=== All examples completed successfully! ===")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure to replace 'your-api-key-here' with your actual API key from https://arca.build")
