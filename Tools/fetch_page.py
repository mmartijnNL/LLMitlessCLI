import requests
from typing import Any

from ..console import print_terminal

from .base_tool import BaseTool
from ..context import Context

class FetchPage(BaseTool):

    @property
    def name(self) -> str:
        return "fetch_page"

    @property
    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Fetch and return the text content of a web page.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the web page to fetch.",
                        },
                    },
                    "required": ["url"],
                },
            },
        }
    
    def invoke(self, context: Context, url: str) -> str:
        try:
            from html.parser import HTMLParser

            class _TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []
                    self._skip = False
                def handle_starttag(self, tag, attrs):
                    if tag in ('script', 'style', 'nav', 'footer'):
                        self._skip = True
                def handle_endtag(self, tag):
                    if tag in ('script', 'style', 'nav', 'footer'):
                        self._skip = False
                def handle_data(self, data):
                    if not self._skip:
                        stripped = data.strip()
                        if stripped:
                            self.text_parts.append(stripped)

            headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            parser = _TextExtractor()
            parser.feed(response.text)
            content = "\n".join(parser.text_parts)
            if len(content) > 8000:
                content = content[:8000] + "\n...[truncated]"
            output = content if content else "[No readable content found]"
            context.conversation.append(
                {
                    "role": "tool",
                    "tool_name": self.name,
                    "content": "\n\n".join(output),
                }
            )
            return output
        except Exception as e:
            return f"Fetch error: {e}"

        