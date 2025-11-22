"""
Examples for using the Arca Tables API
"""

from arca import ArcaTableClient, TableColumn, SkillMetadata


def basic_table_operations(api_key: str):
    """Demonstrate basic table operations"""
    client = ArcaTableClient(user_id=api_key)
    
    # Create a table and insert data
    print("Creating table and inserting data...")
    response = client.upsert(
        table_name="meals",
        columns=[
            TableColumn("food", "VARCHAR"),
            TableColumn("calories", "INTEGER"),
            TableColumn("protein", "DOUBLE"),
            TableColumn("carbs", "DOUBLE"),
            TableColumn("fat", "DOUBLE")
        ],
        data={
            "food": "Grilled Chicken Breast",
            "calories": 165,
            "protein": 31.0,
            "carbs": 0.0,
            "fat": 3.6
        },
        skill=SkillMetadata(
            description="Tracks daily meals and nutritional information",
            examples=[
                "SELECT * FROM meals WHERE calories > 200",
                "SELECT AVG(protein) FROM meals WHERE daysAgo <= 7"
            ],
            notes="Use this table to track nutrition and analyze eating patterns"
        )
    )
    print(f"Response: {response}")
    
    # Add more entries
    print("\nAdding more meal entries...")
    meals = [
        {"food": "Oatmeal with Berries", "calories": 300, "protein": 10.0, "carbs": 54.0, "fat": 6.0},
        {"food": "Greek Yogurt", "calories": 100, "protein": 17.0, "carbs": 6.0, "fat": 0.4},
        {"food": "Salmon Fillet", "calories": 280, "protein": 39.0, "carbs": 0.0, "fat": 13.0},
    ]
    
    for meal in meals:
        client.upsert(table_name="meals", data=meal)
    
    print("Meals added successfully!")


def query_examples(api_key: str):
    """Demonstrate various query options"""
    client = ArcaTableClient(user_id=api_key)
    
    # Simple query with filters
    print("\n1. Query meals with high protein (>20g):")
    results = client.query(
        table_name="meals",
        query="protein > 20",
        order_by="protein DESC"
    )
    print(f"Found {len(results.get('data', []))} results")
    
    # Query with limit and specific columns
    print("\n2. Get top 5 highest calorie meals:")
    results = client.query(
        table_name="meals",
        select=["food", "calories"],
        order_by="calories DESC",
        limit=5
    )
    print(f"Results: {results.get('data', [])}")
    
    # Query with filters dictionary
    print("\n3. Query meals from the last 7 days:")
    results = client.query(
        table_name="meals",
        filters={"daysAgo": 7}
    )
    print(f"Found {len(results.get('data', []))} meals in the last week")
    
    # Aggregation query
    print("\n4. Average nutrition per day:")
    results = client.query(
        table_name="meals",
        select=["DATE(created_at) as date", "AVG(calories) as avg_calories", "AVG(protein) as avg_protein"],
        group_by="DATE(created_at)",
        order_by="date DESC"
    )
    print(f"Daily averages: {results.get('data', [])}")


def update_and_delete_examples(api_key: str):
    """Demonstrate update and delete operations"""
    client = ArcaTableClient(user_id=api_key)
    
    # Update entries
    print("\nUpdating meal calories...")
    result = client.update(
        table_name="meals",
        updates={"calories": 170},
        where="food = 'Grilled Chicken Breast'"
    )
    print(f"Update result: {result}")
    
    # List all tables
    print("\nListing all tables:")
    tables = client.list_tables()
    print(f"Tables: {tables}")
    
    # Get schemas
    print("\nGetting schemas:")
    schemas = client.get_schemas()
    print(f"Schemas: {schemas}")


def skill_management(api_key: str):
    """Demonstrate skill metadata management"""
    client = ArcaTableClient(user_id=api_key)
    
    # Get skill for a table
    print("\nGetting skill metadata...")
    skill = client.get_skill("meals")
    print(f"Current skill: {skill}")
    
    # Update skill metadata
    print("\nUpdating skill metadata...")
    updated_skill = SkillMetadata(
        description="Comprehensive meal tracking with macronutrient analysis",
        examples=[
            "SELECT * FROM meals WHERE calories BETWEEN 200 AND 400",
            "SELECT SUM(protein) FROM meals WHERE daysAgo <= 1"
        ],
        relationships=["Links to workout_sessions table via date"],
        notes="Updated with better examples and relationship information"
    )
    
    result = client.update_skill(table_name="meals", skill=updated_skill)
    print(f"Update result: {result}")
    
    # Get all skills
    print("\nGetting all skills:")
    all_skills = client.get_all_skills()
    print(f"All skills: {all_skills}")


if __name__ == "__main__":
    # Replace with your actual API key from https://arca.build/api-keys
    API_KEY = "your-api-key-here"
    
    print("=== Arca Tables API Examples ===\n")
    
    try:
        basic_table_operations(API_KEY)
        query_examples(API_KEY)
        update_and_delete_examples(API_KEY)
        skill_management(API_KEY)
        
        print("\n=== All examples completed successfully! ===")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure to replace 'your-api-key-here' with your actual API key from https://arca.build/api-keys")
