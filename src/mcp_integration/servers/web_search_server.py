#!/usr/bin/env python3
"""
MCP Web Search Server - Free DuckDuckGo Search

Provides web search capabilities without requiring API keys.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import json

mcp = FastMCP("web-search-server")


@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Use DuckDuckGo HTML search (no API key needed)
        url = "https://html.duckduckgo.com/html/"
        params = {
            "q": query,
            "kl": "us-en"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML results
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # Find search results
        for result in soup.select('.result')[:max_results]:
            try:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                url_elem = result.select_one('.result__url')

                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    result_url = url_elem.get('href') if url_elem else ''

                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': result_url
                    })
            except Exception as e:
                continue

        if not results:
            return f"No results found for: {query}"

        # Format results
        output = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. **{result['title']}**\n"
            output += f"   {result['snippet']}\n"
            if result['url']:
                output += f"   URL: {result['url']}\n"
            output += "\n"

        return output

    except Exception as e:
        return f"Error searching web: {str(e)}"


@mcp.tool()
def get_page_content(url: str) -> str:
    """
    Fetch and extract main text content from a web page

    Args:
        url: URL of the web page to fetch
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Limit to first 2000 characters
        if len(text) > 2000:
            text = text[:2000] + "..."

        return f"Content from {url}:\n\n{text}"

    except Exception as e:
        return f"Error fetching page: {str(e)}"


if __name__ == "__main__":
    # Run the server
    mcp.run()
