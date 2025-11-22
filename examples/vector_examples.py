"""
Examples for using the Arca Vectors API
"""

from arca import ArcaVectorClient, VectorSkillMetadata, MetadataField


def basic_vector_operations(api_key: str):
    """Demonstrate basic vector operations"""
    client = ArcaVectorClient(user_id=api_key)
    
    # Add vector entries with automatic embedding generation
    print("Adding vector entries...")
    
    journal_entries = [
        {
            "text": "Today was incredibly productive. Finished the big project ahead of schedule and felt great about it.",
            "metadata": {"category": "personal", "mood": "positive", "tags": "productivity,achievement"}
        },
        {
            "text": "Had a relaxing day at the beach. The weather was perfect and I felt completely at peace.",
            "metadata": {"category": "personal", "mood": "positive", "tags": "relaxation,vacation"}
        },
        {
            "text": "Struggled with some challenging bugs today. Felt frustrated but learned a lot in the process.",
            "metadata": {"category": "work", "mood": "neutral", "tags": "learning,challenges"}
        },
        {
            "text": "Great workout session this morning. Hit a new personal record on deadlifts!",
            "metadata": {"category": "health", "mood": "positive", "tags": "fitness,achievement"}
        }
    ]
    
    skill = VectorSkillMetadata(
        description="Personal journal entries with mood and category tracking",
        metadata_fields=[
            MetadataField("category", "string", "Type of journal entry", ["personal", "work", "health"]),
            MetadataField("mood", "string", "Emotional state during entry", ["positive", "neutral", "negative"]),
            MetadataField("tags", "string", "Comma-separated tags for categorization")
        ],
        search_examples=[
            "Find days when I felt accomplished",
            "Show me relaxing moments",
            "What did I learn recently?"
        ],
        filter_examples=[
            "category = 'personal' AND mood = 'positive'",
            "mood = 'positive'",
            "category = 'work'"
        ],
        notes="Use semantic search to find similar emotional states or topics"
    )
    
    # Add the first entry with skill metadata
    response = client.add(
        table_name="journal_entries",
        text=journal_entries[0]["text"],
        metadata=journal_entries[0]["metadata"],
        skill=skill
    )
    print(f"First entry added: {response}")
    
    # Add remaining entries
    for entry in journal_entries[1:]:
        client.add(
            table_name="journal_entries",
            text=entry["text"],
            metadata=entry["metadata"]
        )
    
    print(f"Added {len(journal_entries)} journal entries!")


def search_examples(api_key: str):
    """Demonstrate various search options"""
    client = ArcaVectorClient(user_id=api_key)
    
    # Semantic search for productivity
    print("\n1. Search for productive and successful days:")
    results = client.search(
        table_name="journal_entries",
        query="productive and successful accomplishments",
        limit=3
    )
    print(f"Found {results.get('resultCount', 0)} results:")
    for i, result in enumerate(results.get('results', []), 1):
        print(f"  {i}. {result.get('text')[:80]}... (score: {result.get('score', 0):.3f})")
    
    # Search with metadata filter
    print("\n2. Search for relaxation moments in personal category:")
    results = client.search(
        table_name="journal_entries",
        query="relaxing and peaceful moments",
        limit=5,
        filter="category = 'personal'"
    )
    print(f"Found {results.get('resultCount', 0)} results:")
    for i, result in enumerate(results.get('results', []), 1):
        print(f"  {i}. {result.get('text')[:80]}...")
    
    # Search for learning experiences
    print("\n3. Search for learning and growth:")
    results = client.search(
        table_name="journal_entries",
        query="learning new things and personal growth",
        limit=3
    )
    print(f"Found {results.get('resultCount', 0)} results")
    
    # Search with positive mood filter
    print("\n4. Search positive moments:")
    results = client.search(
        table_name="journal_entries",
        query="happy and joyful experiences",
        filter="mood = 'positive'",
        limit=5
    )
    print(f"Found {results.get('resultCount', 0)} positive moments")


def table_management(api_key: str):
    """Demonstrate table management operations"""
    client = ArcaVectorClient(user_id=api_key)
    
    # List all vector tables
    print("\nListing all vector tables:")
    tables = client.list_tables()
    print(f"Tables: {tables}")
    
    # Get skill for a table
    print("\nGetting skill metadata for journal_entries:")
    skill = client.get_skill("journal_entries")
    print(f"Skill: {skill}")
    
    # Get all skills
    print("\nGetting all vector skills:")
    all_skills = client.get_all_skills()
    print(f"All skills: {all_skills}")


def advanced_examples(api_key: str):
    """Demonstrate advanced vector operations"""
    client = ArcaVectorClient(user_id=api_key)
    
    # Create a knowledge base
    print("\nCreating a knowledge base...")
    
    knowledge_items = [
        {
            "text": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
            "metadata": {"topic": "programming", "language": "python", "difficulty": "beginner"}
        },
        {
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "metadata": {"topic": "ai", "subtopic": "machine-learning", "difficulty": "intermediate"}
        },
        {
            "text": "REST APIs use HTTP requests to GET, PUT, POST and DELETE data, following representational state transfer principles.",
            "metadata": {"topic": "web-development", "subtopic": "api", "difficulty": "intermediate"}
        }
    ]
    
    skill = VectorSkillMetadata(
        description="Programming and technology knowledge base",
        metadata_fields=[
            MetadataField("topic", "string", "Main topic area", ["programming", "ai", "web-development"]),
            MetadataField("difficulty", "string", "Difficulty level", ["beginner", "intermediate", "advanced"])
        ],
        search_examples=["Explain Python basics", "What is machine learning?"],
        filter_examples=["difficulty = 'beginner'", "topic = 'ai'"]
    )
    
    for item in knowledge_items:
        client.add(
            table_name="knowledge_base",
            text=item["text"],
            metadata=item["metadata"],
            skill=skill if item == knowledge_items[0] else None
        )
    
    print(f"Added {len(knowledge_items)} knowledge items!")
    
    # Search the knowledge base
    print("\nSearching knowledge base for 'how to build web APIs':")
    results = client.search(
        table_name="knowledge_base",
        query="how to build web APIs",
        limit=2
    )
    
    for i, result in enumerate(results.get('results', []), 1):
        print(f"\n  Result {i}:")
        print(f"  Text: {result.get('text')}")
        print(f"  Metadata: {result.get('metadata')}")
        print(f"  Similarity: {result.get('score', 0):.3f}")


if __name__ == "__main__":
    # Replace with your actual API key from https://arca.build/api-keys
    API_KEY = "your-api-key-here"
    
    print("=== Arca Vectors API Examples ===\n")
    
    try:
        basic_vector_operations(API_KEY)
        search_examples(API_KEY)
        table_management(API_KEY)
        advanced_examples(API_KEY)
        
        print("\n=== All examples completed successfully! ===")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure to replace 'your-api-key-here' with your actual API key from https://arca.build/api-keys")
