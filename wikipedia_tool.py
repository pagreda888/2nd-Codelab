import requests


def search_wikipedia(query: str) -> dict:
    """Searches Wikipedia for a given term and returns a brief summary.

    Args:
        query: The search term (e.g., 'Aspirin').

    Returns:
        A dictionary containing the page 'title', 'extract' (summary), and 'content_urls'.
    """
    clean_query = query.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", query),
                "summary": data.get("extract", "No summary found."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        return {"error": f"Wikipedia page not found (Status Code: {response.status_code})"}
    except Exception as e:
        return {"error": f"Failed to reach Wikipedia: {e}"}
