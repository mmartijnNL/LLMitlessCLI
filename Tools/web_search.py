
from typing import Any

from .base_tool import BaseTool
from ..context import Context
from ddgs import DDGS

class WebSearch(BaseTool):

    maxResults = 5

    @property
    def name(self) -> str:
        return "web-search"

    @property
    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Search the web using DuckDuckGo and return short result summaries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string.",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return.",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    def invoke(self, context: Context, query: str, max_results: int = 5) -> str:

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No results found."
            output = []
            for i, r in enumerate(results, 1):
                output.append(f"{i}. {r.get('title', 'No title')}\n   URL: {r.get('href', '')}\n   {r.get('body', '')}")
            
            
            context.conversation.append(
                {
                    "role": "tool",
                    "tool_name": self.name,
                    "content": "\n\n".join(output),
                }
            )
            
            return "\n\n".join(output)
        except Exception as e:
            return f"Search error: {e}"
        