#!/usr/bin/env python
"""
Test read_webpage function with various websites including challenging ones.

This script demonstrates how to use the read_webpage function with:
- Wikipedia articles
- News sites
- E-commerce sites
- API endpoints
- Sites requiring custom headers/cookies

Note: Requires OPENROUTER_API_KEY environment variable to be set.
"""

import fundas as fd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_wikipedia_article():
    """Test extracting data from a Wikipedia article about Python."""
    print("=" * 60)
    print("Test 1: Python Programming Language Wikipedia Article")
    print("=" * 60)

    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    prompt = "Extract key information about Python programming language"
    columns = ["feature", "description"]

    try:
        df = fd.read_webpage(url, prompt=prompt, columns=columns)
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_wikipedia_historical_figure():
    """Test extracting data from a Wikipedia article about a historical figure."""
    print("=" * 60)
    print("Test 2: Albert Einstein Wikipedia Article")
    print("=" * 60)

    url = "https://en.wikipedia.org/wiki/Albert_Einstein"
    prompt = "Extract key facts about Albert Einstein's life and achievements"
    columns = ["category", "fact"]

    try:
        df = fd.read_webpage(url, prompt=prompt, columns=columns)
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_wikipedia_country():
    """Test extracting data from a Wikipedia article about a country."""
    print("=" * 60)
    print("Test 3: Japan Wikipedia Article")
    print("=" * 60)

    url = "https://en.wikipedia.org/wiki/Japan"
    prompt = "Extract basic information about Japan"
    columns = ["attribute", "value"]

    try:
        df = fd.read_webpage(url, prompt=prompt, columns=columns)
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_wikipedia_with_custom_prompt():
    """Test with a more specific custom prompt."""
    print("=" * 60)
    print("Test 4: Extracting Specific Data - Machine Learning Article")
    print("=" * 60)

    url = "https://en.wikipedia.org/wiki/Machine_learning"
    prompt = (
        "Extract the main types/categories of machine learning "
        "mentioned in this article along with their brief descriptions"
    )
    columns = ["type", "description", "examples"]

    try:
        df = fd.read_webpage(url, prompt=prompt, columns=columns)
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_news_site():
    """Test extracting data from a news site (BBC)."""
    print("=" * 60)
    print("Test 5: BBC News Homepage")
    print("=" * 60)

    url = "https://www.bbc.com/news"
    prompt = "Extract the main headlines and their brief summaries"
    columns = ["headline", "summary", "category"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            timeout=60,  # Longer timeout for news sites
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_github_repo():
    """Test extracting data from GitHub."""
    print("=" * 60)
    print("Test 6: GitHub Repository Page")
    print("=" * 60)

    url = "https://github.com/pandas-dev/pandas"
    prompt = "Extract repository statistics and information"
    columns = ["metric", "value"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            headers={
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
            },
        )
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_stackoverflow():
    """Test extracting data from Stack Overflow."""
    print("=" * 60)
    print("Test 7: Stack Overflow Questions")
    print("=" * 60)

    url = "https://stackoverflow.com/questions/tagged/python?tab=votes&pagesize=15"
    prompt = "Extract the top questions with their vote counts and answer counts"
    columns = ["question", "votes", "answers", "views"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            retry_count=3,
            retry_delay=2.0,
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_imdb():
    """Test extracting data from IMDB."""
    print("=" * 60)
    print("Test 8: IMDB Top Movies")
    print("=" * 60)

    url = "https://www.imdb.com/chart/top/"
    prompt = "Extract the top 10 movies with their ratings and year"
    columns = ["rank", "title", "year", "rating"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            headers={
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_hacker_news():
    """Test extracting data from Hacker News."""
    print("=" * 60)
    print("Test 9: Hacker News Front Page")
    print("=" * 60)

    url = "https://news.ycombinator.com/"
    prompt = "Extract the top stories with their titles, points, and comment counts"
    columns = ["rank", "title", "points", "comments", "source"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_reddit():
    """Test extracting data from Reddit (old interface for better scraping)."""
    print("=" * 60)
    print("Test 10: Reddit r/Python")
    print("=" * 60)

    url = "https://old.reddit.com/r/Python/top/?t=week"
    prompt = "Extract the top posts with their titles, upvotes, and comment counts"
    columns = ["title", "upvotes", "comments", "author"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            timeout=45,
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_arxiv():
    """Test extracting data from arXiv."""
    print("=" * 60)
    print("Test 11: arXiv Recent AI Papers")
    print("=" * 60)

    url = "https://arxiv.org/list/cs.AI/recent"
    prompt = "Extract recent paper titles with their authors and submission dates"
    columns = ["title", "authors", "date", "abstract_preview"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
        )
        print("\nExtracted Data:")
        print(df.head(10))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_public_api():
    """Test extracting data from a public JSON API."""
    print("=" * 60)
    print("Test 12: JSONPlaceholder API (Public Test API)")
    print("=" * 60)

    url = "https://jsonplaceholder.typicode.com/posts"
    prompt = "Extract posts with their titles and bodies"
    columns = ["id", "title", "body"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            headers={
                "Accept": "application/json",
            },
        )
        print("\nExtracted Data:")
        print(df.head(5))
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_with_custom_headers():
    """Test with custom headers to bypass restrictions."""
    print("=" * 60)
    print("Test 13: Custom Headers Example (httpbin.org)")
    print("=" * 60)

    url = "https://httpbin.org/headers"
    prompt = "Extract the headers information"
    columns = ["header_name", "header_value"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            headers={
                "X-Custom-Header": "CustomValue123",
                "Authorization": "Bearer test-token",
                "X-Request-ID": "fundas-test-001",
            },
        )
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_with_ssl_skip():
    """Test with SSL verification disabled (useful for self-signed certs)."""
    print("=" * 60)
    print("Test 14: SSL Test (with verification)")
    print("=" * 60)

    url = "https://httpbin.org/get"
    prompt = "Extract the request information"
    columns = ["field", "value"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            verify_ssl=True,  # Set to False for self-signed certificates
        )
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_post_request():
    """Test POST request with payload."""
    print("=" * 60)
    print("Test 15: POST Request (httpbin.org)")
    print("=" * 60)

    url = "https://httpbin.org/post"
    prompt = "Extract the posted data and form fields"
    columns = ["field", "value"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            method="POST",
            payload={
                "username": "testuser",
                "email": "test@example.com",
                "message": "Hello from fundas!",
            },
        )
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def test_with_cookies():
    """Test request with cookies."""
    print("=" * 60)
    print("Test 16: Request with Cookies (httpbin.org)")
    print("=" * 60)

    url = "https://httpbin.org/cookies"
    prompt = "Extract the cookie information"
    columns = ["cookie_name", "cookie_value"]

    try:
        df = fd.read_webpage(
            url,
            prompt=prompt,
            columns=columns,
            cookies={
                "session_id": "abc123xyz",
                "user_pref": "dark_mode",
                "tracking_id": "fundas_test_001",
            },
        )
        print("\nExtracted Data:")
        print(df)
        print(f"\nShape: {df.shape}")
    except Exception as e:
        print(f"Error: {e}")

    print()


def main():
    print("\n" + "=" * 60)
    print("Fundas read_webpage Advanced Testing Suite")
    print("=" * 60 + "\n")

    # Check if API key is available
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set!")
        print("   Set it with: export OPENROUTER_API_KEY='your-api-key'")
        print("   Or add it to your .env file")
        return

    print(f"✓ API Key found (starts with: {api_key[:8]}...)")
    print(f"✓ Using fundas version: {fd.__version__}")
    print()

    print("Available test options:")
    print("  1. Wikipedia - Python article")
    print("  2. Wikipedia - Albert Einstein")
    print("  3. Wikipedia - Japan")
    print("  4. Wikipedia - Machine Learning")
    print("  5. BBC News")
    print("  6. GitHub Repository")
    print("  7. Stack Overflow")
    print("  8. IMDB Top Movies")
    print("  9. Hacker News")
    print("  10. Reddit r/Python")
    print("  11. arXiv AI Papers")
    print("  12. Public JSON API")
    print("  13. Custom Headers Test")
    print("  14. SSL Test")
    print("  15. POST Request Test")
    print("  16. Cookies Test")
    print("  all. Run all tests")
    print()

    choice = (
        input("Enter test number(s) separated by comma, or 'all': ").strip().lower()
    )

    if choice == "all":
        tests = range(1, 17)
    else:
        try:
            tests = [int(x.strip()) for x in choice.split(",")]
        except ValueError:
            print("Invalid input. Running all Wikipedia tests.")
            tests = [1, 2, 3, 4]

    test_functions = {
        1: test_wikipedia_article,
        2: test_wikipedia_historical_figure,
        3: test_wikipedia_country,
        4: test_wikipedia_with_custom_prompt,
        5: test_news_site,
        6: test_github_repo,
        7: test_stackoverflow,
        8: test_imdb,
        9: test_hacker_news,
        10: test_reddit,
        11: test_arxiv,
        12: test_public_api,
        13: test_with_custom_headers,
        14: test_with_ssl_skip,
        15: test_post_request,
        16: test_with_cookies,
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
