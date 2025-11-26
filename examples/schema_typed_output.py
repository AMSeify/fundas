#!/usr/bin/env python
"""
Test structured output with schema-based type enforcement.

This script demonstrates how to use the Schema feature to get
properly typed data from various sources (webpage, PDF, image, etc.)

Note: Requires OPENROUTER_API_KEY environment variable to be set.
"""

import fundas as fd
from fundas import Schema, Column, DataType
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_schema_basic():
    """Test basic schema creation and type definitions."""
    print("=" * 60)
    print("Test 1: Basic Schema Creation")
    print("=" * 60)

    # Using Column objects
    schema1 = Schema(
        [
            Column("name", DataType.STRING, description="Product name"),
            Column("price", DataType.FLOAT, description="Price in USD"),
            Column("quantity", DataType.INTEGER, description="Stock quantity"),
            Column("in_stock", DataType.BOOLEAN, description="Availability status"),
        ]
    )
    print(f"\nSchema 1: {schema1}")
    print(f"Column names: {schema1.get_column_names()}")

    # Using shorthand dict format
    schema2 = Schema(
        {
            "name": "string",
            "price": "float",
            "quantity": "int",
            "available": "bool",
        }
    )
    print(f"\nSchema 2: {schema2}")
    print(f"Column names: {schema2.get_column_names()}")

    # Print JSON schema for API
    print("\nJSON Schema for API:")
    import json

    print(json.dumps(schema1.to_json_schema(), indent=2))

    print()


def test_webpage_with_schema():
    """Test webpage extraction with typed schema."""
    print("=" * 60)
    print("Test 2: Webpage Extraction with Schema (Wikipedia)")
    print("=" * 60)

    # Define schema for country data
    schema = Schema(
        [
            Column("attribute", DataType.STRING, description="Country attribute name"),
            Column("value", DataType.STRING, description="Attribute value"),
        ],
        name="country_data",
    )

    url = "https://en.wikipedia.org/wiki/France"
    prompt = "Extract basic facts about France (capital, population, area, language)"

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df)
        print(f"\nData types:\n{df.dtypes}")
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_webpage_with_numeric_schema():
    """Test webpage extraction with numeric types."""
    print("=" * 60)
    print("Test 3: Webpage with Numeric Types (Hacker News)")
    print("=" * 60)

    # Schema with different numeric types
    schema = Schema(
        [
            Column("rank", DataType.INTEGER, description="Story rank position"),
            Column("title", DataType.STRING, description="Story title"),
            Column(
                "points", DataType.INTEGER, description="Upvote points", nullable=True
            ),
            Column(
                "comments",
                DataType.INTEGER,
                description="Number of comments",
                nullable=True,
            ),
        ],
        name="hacker_news_stories",
    )

    url = "https://news.ycombinator.com/"
    prompt = (
        "Extract the top 10 stories with their ranks, titles, "
        "points, and comment counts"
    )

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nData types:\n{df.dtypes}")

        # Demonstrate numeric operations work correctly
        if "points" in df.columns and df["points"].notna().any():
            print(f"\nTotal points: {df['points'].sum()}")
            print(f"Average points: {df['points'].mean():.2f}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_webpage_with_date_schema():
    """Test webpage extraction with date types."""
    print("=" * 60)
    print("Test 4: Webpage with Date Types (arXiv)")
    print("=" * 60)

    # Schema with date type
    schema = Schema(
        [
            Column("title", DataType.STRING, description="Paper title"),
            Column("authors", DataType.STRING, description="Paper authors"),
            Column(
                "submitted_date",
                DataType.DATE,
                description="Submission date (YYYY-MM-DD)",
            ),
        ],
        name="arxiv_papers",
    )

    url = "https://arxiv.org/list/cs.AI/recent"
    prompt = "Extract recent AI papers with their titles, authors, and submission dates"

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df.head(5))
        print(f"\nData types:\n{df.dtypes}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_webpage_with_float_schema():
    """Test webpage extraction with float types."""
    print("=" * 60)
    print("Test 5: Webpage with Float Types (httpbin)")
    print("=" * 60)

    # Schema with float type for testing numeric conversion
    schema = Schema(
        [
            Column("metric_name", DataType.STRING, description="Name of the metric"),
            Column(
                "metric_value",
                DataType.FLOAT,
                description="Numeric value",
                nullable=True,
            ),
        ],
        name="metrics",
    )

    url = "https://httpbin.org/json"
    prompt = (
        "Extract any key-value pairs from this JSON, treating numeric values as floats"
    )

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df)
        print(f"\nData types:\n{df.dtypes}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_wikipedia_movie_with_schema():
    """Test Wikipedia movie page with complex schema."""
    print("=" * 60)
    print("Test 6: Wikipedia Movie Data with Schema")
    print("=" * 60)

    # Complex schema for movie data
    schema = Schema(
        [
            Column("attribute", DataType.STRING, description="Movie attribute"),
            Column("value", DataType.STRING, description="Attribute value"),
        ],
        name="movie_info",
    )

    url = "https://en.wikipedia.org/wiki/The_Matrix"
    prompt = (
        "Extract movie information: title, director, release year, "
        "runtime in minutes, box office gross, genre, and main cast"
    )

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_json_api_with_schema():
    """Test JSON API extraction with schema."""
    print("=" * 60)
    print("Test 7: JSON API with Schema (JSONPlaceholder)")
    print("=" * 60)

    # Schema for API data
    schema = Schema(
        [
            Column("id", DataType.INTEGER, description="User ID"),
            Column("name", DataType.STRING, description="User name"),
            Column("email", DataType.STRING, description="Email address"),
            Column("company", DataType.STRING, description="Company name"),
        ],
        name="users",
    )

    url = "https://jsonplaceholder.typicode.com/users"
    prompt = "Extract user information with their ID, name, email, and company name"

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df)
        print(f"\nData types:\n{df.dtypes}")

        # Verify ID is actually an integer
        if "id" in df.columns:
            print(f"\nID column type: {df['id'].dtype}")
            print(f"ID values: {df['id'].tolist()}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_shorthand_schema():
    """Test shorthand schema format."""
    print("=" * 60)
    print("Test 8: Shorthand Schema Format")
    print("=" * 60)

    # Using dict shorthand for quick schema definition
    shorthand_schema = Schema(
        {
            "name": "string",
            "founded": "integer",
            "description": "string",
        }
    )

    url = "https://en.wikipedia.org/wiki/IMDB"
    prompt = "Extract information about IMDB (what it is, when founded, key facts)"

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            schema=shorthand_schema,  # Use the shorthand schema
        )
        print("\nExtracted Data:")
        print(df.head(5))
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_nullable_columns():
    """Test schema with nullable columns."""
    print("=" * 60)
    print("Test 9: Nullable Columns")
    print("=" * 60)

    # Schema with nullable columns
    schema = Schema(
        [
            Column("name", DataType.STRING, description="Item name"),
            Column("price", DataType.FLOAT, description="Current price", nullable=True),
            Column(
                "discount_price",
                DataType.FLOAT,
                description="Discounted price if any",
                nullable=True,
            ),
            Column(
                "rating", DataType.FLOAT, description="User rating 1-5", nullable=True
            ),
        ],
        name="products",
    )

    url = "https://en.wikipedia.org/wiki/E-commerce"
    prompt = (
        "Extract example products/items mentioned with their prices and ratings. "
        "Use null for missing values."
    )

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df)
        print(f"\nData types:\n{df.dtypes}")
        print(f"\nNull counts:\n{df.isnull().sum()}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_enum_column():
    """Test schema with enum (allowed values) constraint."""
    print("=" * 60)
    print("Test 10: Enum Column (Status Values)")
    print("=" * 60)

    # Schema with enum constraint
    schema = Schema(
        [
            Column("feature", DataType.STRING, description="Feature name"),
            Column(
                "status",
                DataType.STRING,
                description="Feature status",
                enum_values=["stable", "beta", "experimental", "deprecated"],
            ),
            Column("version", DataType.STRING, description="Version introduced"),
        ],
        name="features",
    )

    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    prompt = (
        "Extract Python features/modules with their status "
        "(stable, beta, experimental, or deprecated) and version"
    )

    try:
        df = fd.read_webpage(url, prompt=prompt, schema=schema)
        print("\nExtracted Data:")
        print(df.head(10))
        if "status" in df.columns:
            print(f"\nUnique status values: {df['status'].unique()}")
        else:
            print("\nUnique status values: N/A")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_type_conversion_demo():
    """Demonstrate type conversion capabilities."""
    print("=" * 60)
    print("Test 11: Type Conversion Demonstration")
    print("=" * 60)

    # Create a Column and test conversion
    from fundas.schema import Column, DataType

    # Integer conversion
    int_col = Column("test_int", DataType.INTEGER)
    print("Integer conversions:")
    for val in ["42", "3.14", "1,000", None, "invalid"]:
        result = int_col.convert_value(val)
        print(f"  '{val}' -> {result} (type: {type(result).__name__})")

    # Float conversion
    float_col = Column("test_float", DataType.FLOAT)
    print("\nFloat conversions:")
    for val in ["3.14", "42", "1,234.56", None]:
        result = float_col.convert_value(val)
        print(f"  '{val}' -> {result} (type: {type(result).__name__})")

    # Boolean conversion
    bool_col = Column("test_bool", DataType.BOOLEAN)
    print("\nBoolean conversions:")
    for val in ["true", "false", "yes", "no", "1", "0", True, False]:
        result = bool_col.convert_value(val)
        print(f"  '{val}' -> {result} (type: {type(result).__name__})")

    # Date conversion
    date_col = Column("test_date", DataType.DATE)
    print("\nDate conversions:")
    for val in ["2024-01-15", "15/01/2024", "01-15-2024", None]:
        result = date_col.convert_value(val)
        print(f"  '{val}' -> {result} (type: {type(result).__name__})")

    print()


def main():
    print("\n" + "=" * 60)
    print("Fundas Structured Output Test Suite")
    print("=" * 60 + "\n")

    # Check if API key is available
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set!")
        print("   Set it with: export OPENROUTER_API_KEY='your-api-key'")
        print("   Or add it to your .env file")
        print("\n   Running local tests only...\n")
        test_schema_basic()
        test_type_conversion_demo()
        return

    print(f"✓ API Key found (starts with: {api_key[:8]}...)")
    print(f"✓ Using fundas version: {fd.__version__}")
    print()

    print("Available tests:")
    print("  1. Basic Schema Creation (local)")
    print("  2. Webpage with Schema (Wikipedia - France)")
    print("  3. Webpage with Numeric Types (Hacker News)")
    print("  4. Webpage with Date Types (arXiv)")
    print("  5. Webpage with Float Types (httpbin)")
    print("  6. Wikipedia Movie Data (The Matrix)")
    print("  7. JSON API with Schema (JSONPlaceholder)")
    print("  8. Shorthand Schema Format")
    print("  9. Nullable Columns")
    print("  10. Enum Column (Status Values)")
    print("  11. Type Conversion Demo (local)")
    print("  all. Run all tests")
    print()

    choice = (
        input("Enter test number(s) separated by comma, or 'all': ").strip().lower()
    )

    if choice == "all":
        tests = range(1, 12)
    else:
        try:
            tests = [int(x.strip()) for x in choice.split(",")]
        except ValueError:
            print("Invalid input. Running basic tests.")
            tests = [1, 11]

    test_functions = {
        1: test_schema_basic,
        2: test_webpage_with_schema,
        3: test_webpage_with_numeric_schema,
        4: test_webpage_with_date_schema,
        5: test_webpage_with_float_schema,
        6: test_wikipedia_movie_with_schema,
        7: test_json_api_with_schema,
        8: test_shorthand_schema,
        9: test_nullable_columns,
        10: test_enum_column,
        11: test_type_conversion_demo,
    }

    print()
    for test_num in tests:
        if test_num in test_functions:
            test_functions[test_num]()

    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
