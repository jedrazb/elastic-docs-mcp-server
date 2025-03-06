import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Setup Elasticsearch client
es_client = Elasticsearch(os.getenv("ES_URL"), api_key=os.getenv("API_KEY"))

# Initialize FastMCP server
mcp = FastMCP("Search Labs Blog Search MCP", dependencies=["elasticsearch"])


# Elasticsearch search function
def search_search_labs(query: str) -> list[dict]:
    """Perform semantic search on Search Labs blog posts."""
    try:
        results = es_client.search(
            index="search-labs-posts",
            body={
                "query": {
                    "semantic": {"query": query, "field": "semantic_body"},
                },
                "_source": [
                    "title",
                    "url",
                    "semantic_body.inference.chunks.text",
                ],
                "size": 5,
            },
        )
        return [
            {
                "title": hit["_source"].get("title", ""),
                "url": hit["_source"].get("url", ""),
                "content": [
                    chunk.get("text", "")
                    for chunk in hit["_source"]
                    .get("semantic_body", {})
                    .get("inference", {})
                    .get("chunks", [])[:3]
                ],
            }
            for hit in results.get("hits", {}).get("hits", [])
        ]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


# MCP tool for documentation search
@mcp.tool(
    name="search_search_labs_blog",
    description="Perform a semantic search across Search Labs blog posts for a given query.",
)
def search_search_labs_blog(query: str) -> str:
    """Returns formatted search results from Search Labs blog posts."""
    results = search_search_labs(query)
    return (
        "\n\n".join(
            [
                f"### {hit['title']}\n[Read More]({hit['url']})\n- {hit['content']}"
                for hit in results
            ]
        )
        if results
        else "No results found."
    )


# Start MCP server
if __name__ == "__main__":
    print(f"MCP server '{mcp.name}' is running...")
    mcp.run()
