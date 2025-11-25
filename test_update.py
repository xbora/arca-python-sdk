
"""
Test script to verify the Arca SDK update() function works correctly
"""

from arca import ArcaTableClient, TableColumn
import os

# Replace with your actual API key or use environment variable
API_KEY = os.getenv("ARCA_API_KEY", "your-api-key-here")

def test_update_function():
    """Test the SDK update function with correct parameters"""
    client = ArcaTableClient(user_id=API_KEY)
    
    print("=" * 60)
    print("Testing Arca SDK update() function")
    print("=" * 60)
    
    # First, create a test table and insert some data
    print("\n1. Creating test table and inserting data...")
    try:
        response = client.upsert(
            table_name="test_crm_deals",
            columns=[
                TableColumn("id", "INTEGER"),
                TableColumn("value", "INTEGER"),
                TableColumn("probability", "INTEGER"),
                TableColumn("deal_name", "VARCHAR")
            ],
            data={
                "id": 1,
                "value": 50000,
                "probability": 25,
                "deal_name": "Test Deal"
            }
        )
        print(f"✅ Table created and data inserted: {response}")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return
    
    # Test update with CORRECT format (dict for where)
    print("\n2. Testing update with CORRECT format (where as dict)...")
    try:
        result = client.update(
            table_name="test_crm_deals",
            data={"value": 100000, "probability": 50},
            where={"id": 1}  # ✅ CORRECT: dict for exact match
        )
        print(f"✅ Update successful: {result}")
    except Exception as e:
        print(f"❌ Update failed: {e}")
    
    # Query to verify the update
    print("\n3. Querying to verify update...")
    try:
        results = client.query(table_name="test_crm_deals")
        print(f"✅ Query results: {results.get('data', [])}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test update with INCORRECT format (string for where) - should fail
    print("\n4. Testing update with INCORRECT format (where as string)...")
    try:
        result = client.update(
            table_name="test_crm_deals",
            data={"probability": 75},
            where="id=1"  # ❌ INCORRECT: This is what the MCP server is doing
        )
        print(f"⚠️ Update with string where succeeded (unexpected): {result}")
    except Exception as e:
        print(f"✅ Update with string where failed as expected: {e}")
    
    # Cleanup
    print("\n5. Cleaning up test table...")
    try:
        client.delete(table_name="test_crm_deals")
        print("✅ Test table deleted")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("The SDK expects where={'id': 1} (dict)")
    print("The MCP server is sending where='id=1' (string)")
    print("This mismatch is causing the 500 error.")


if __name__ == "__main__":
    test_update_function()
