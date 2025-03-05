import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Setup Elasticsearch client
es_client = Elasticsearch(os.getenv("ES_URL"), api_key=os.getenv("API_KEY"))

# Initialize FastMCP server
mcp = FastMCP("Elastic Demo MCP Server", dependencies=["elasticsearch"])


# Elasticsearch search function
def search_elastic_docs(query: str) -> list[dict]:
    """Perform semantic search on Elastic documentation."""
    try:
        results = es_client.search(
            index="search-elastic-docs",
            body={
                "query": {
                    "semantic": {"query": query, "field": "semantic_body_content"}
                },
                "_source": [
                    "title",
                    "url",
                    "semantic_body_content.inference.chunks.text",
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
                    .get("semantic_body_content", {})
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
    name="search_elasticsearch_documentation",
    description="Perform a semantic search across Elastic documentation for a given query.",
)
def search_elasticsearch_documentation(query: str) -> str:
    """Returns formatted search results from Elasticsearch documentation."""
    results = search_elastic_docs(query)
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
