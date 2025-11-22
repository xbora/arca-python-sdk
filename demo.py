"""
Demo script for Arca Python SDK

This script demonstrates the structure and usage of the Arca SDK.
To use with a real API, replace the API_KEY variable with your actual key from https://arca.fyi/api-keys
"""

from arca import (
    ArcaTableClient,
    ArcaVectorClient,
    TableColumn,
    SkillMetadata,
    VectorSkillMetadata,
    MetadataField,
    __version__
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_package_info():
    """Display package information"""
    print_section("Arca Python SDK - Package Information")
    print(f"Version: {__version__}")
    print(f"Author: Arca Team")
    print(f"Website: https://arca.fyi")
    print(f"\nThis SDK provides access to:")
    print(f"  • Tables API - Store structured data (like SQL)")
    print(f"  • Vectors API - Store & search unstructured data semantically")


def demo_table_client_structure():
    """Demonstrate the ArcaTableClient structure"""
    print_section("Table Client - Structure & Methods")
    
    print("Available Methods:")
    methods = [
        "upsert(table_name, data, columns=None, skill=None)",
        "query(table_name, filters=None, limit=None, order_by=None, ...)",
        "update(table_name, updates, where=None, filters=None)",
        "delete(table_name)",
        "list_tables()",
        "get_schemas()",
        "get_skill(table_name)",
        "update_skill(table_name, skill)",
        "get_all_skills()",
        "export(table_name)"
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"  {i}. {method}")
    
    print("\nSupported Column Types:")
    types = ["VARCHAR", "INTEGER", "BIGINT", "DOUBLE", "BOOLEAN", "TIMESTAMP", "DATE", "JSON"]
    print(f"  {', '.join(types)}")


def demo_vector_client_structure():
    """Demonstrate the ArcaVectorClient structure"""
    print_section("Vector Client - Structure & Methods")
    
    print("Available Methods:")
    methods = [
        "add(table_name, text, metadata=None, skill=None)",
        "search(table_name, query, limit=5, filter=None)",
        "delete(table_name)",
        "list_tables()",
        "get_skill(table_name)",
        "update_skill(table_name, skill)",
        "get_all_skills()",
        "export(table_name)"
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"  {i}. {method}")
    
    print("\nKey Features:")
    print(f"  • Automatic embedding generation")
    print(f"  • Semantic similarity search")
    print(f"  • Metadata filtering")
    print(f"  • Custom skill descriptions for AI assistants")


def demo_data_models():
    """Demonstrate the data model classes"""
    print_section("Data Models")
    
    print("1. TableColumn - Define table schema:")
    col = TableColumn(name="age", type="INTEGER", nullable=False)
    print(f"   Example: {col}")
    print(f"   As dict: {col.to_dict()}")
    
    print("\n2. SkillMetadata - Help AI understand tables:")
    skill = SkillMetadata(
        description="User profiles with demographics",
        examples=["SELECT * FROM users WHERE age > 25"],
        notes="Contains sensitive PII data"
    )
    print(f"   Example: {skill.description}")
    
    print("\n3. VectorSkillMetadata - Help AI search vectors:")
    vector_skill = VectorSkillMetadata(
        description="Document embeddings for semantic search",
        search_examples=["Find documents about machine learning"],
        filter_examples=["category = 'technical'"]
    )
    print(f"   Example: {vector_skill.description}")
    
    print("\n4. MetadataField - Define vector metadata schema:")
    field = MetadataField(
        name="category",
        type="string",
        description="Document category",
        examples=["technical", "business", "personal"]
    )
    print(f"   Example: {field.name} - {field.description}")


def demo_usage_example():
    """Show a complete usage example"""
    print_section("Usage Example (Structure Only)")
    
    print("# Initialize clients:")
    print('table_client = ArcaTableClient(user_id="your-api-key")')
    print('vector_client = ArcaVectorClient(user_id="your-api-key")')
    
    print("\n# Create a table and insert data:")
    print('table_client.upsert(')
    print('    table_name="meals",')
    print('    columns=[TableColumn("food", "VARCHAR"), TableColumn("calories", "INTEGER")],')
    print('    data={"food": "Pizza", "calories": 800}')
    print(')')
    
    print("\n# Query the table:")
    print('results = table_client.query(')
    print('    table_name="meals",')
    print('    filters={"daysAgo": 7},')
    print('    order_by="calories DESC",')
    print('    limit=10')
    print(')')
    
    print("\n# Add vector entry:")
    print('vector_client.add(')
    print('    table_name="notes",')
    print('    text="Remember to buy groceries tomorrow",')
    print('    metadata={"category": "personal", "priority": "high"}')
    print(')')
    
    print("\n# Search vectors semantically:")
    print('results = vector_client.search(')
    print('    table_name="notes",')
    print('    query="shopping tasks",')
    print('    limit=5,')
    print('    filter="priority = \'high\'"')
    print(')')


def demo_error_handling():
    """Demonstrate error handling"""
    print_section("Error Handling")
    
    print("The SDK provides custom exceptions:")
    print("\n1. ArcaAuthError - Authentication failures")
    print("   Raised when API key is invalid or missing")
    
    print("\n2. ArcaAPIError - API request failures")
    print("   Includes status_code and error message")
    
    print("\n3. ArcaValidationError - Request validation failures")
    print("   Raised when request parameters are invalid")
    
    print("\nExample:")
    print("try:")
    print("    client.query(table_name='meals')")
    print("except ArcaAuthError as e:")
    print("    print(f'Auth failed: {e}')")
    print("except ArcaAPIError as e:")
    print("    print(f'API error: {e.message} (status: {e.status_code})')")


def main():
    """Main demo function"""
    print("\n" + "="*60)
    print(" "*15 + "ARCA PYTHON SDK DEMO")
    print("="*60)
    
    demo_package_info()
    demo_table_client_structure()
    demo_vector_client_structure()
    demo_data_models()
    demo_usage_example()
    demo_error_handling()
    
    print_section("Getting Started")
    print("1. Get your API key from: https://arca.fyi/api-keys")
    print("2. Install the SDK: pip install arca-sdk")
    print("3. Check out the examples/ directory for complete working examples")
    print("4. Read the full documentation at: https://docs.arca.fyi")
    
    print("\n" + "="*60)
    print("  Demo completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
