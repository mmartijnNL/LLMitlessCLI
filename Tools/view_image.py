
from importlib.resources import path
import os
from typing import Any

from .base_tool import BaseTool
from ..context import Context

class ViewImage(BaseTool):

    maxResults = 5

    @property
    def name(self) -> str:
        return "view-image"

    @property
    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Load a local image file so you can analyse its contents. Keep it short.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Absolute or relative path to the image file.",
                        },
                    },
                    "required": ["path"],
                },
            },
        }

    def invoke(self, context: Context, path: str, max_results: int = 5) -> str:

        try:
            expanded = os.path.expanduser(path.strip())
            resolved = expanded if os.path.isabs(expanded) else os.path.normpath(os.path.join(context.directory, expanded))
            if not os.path.isfile(resolved):
                return f"Error: file not found: {resolved}"
            
            img_message: dict = {"role": "user", "content": "[images attached for your analysis]"}
            img_message["images"] = [resolved]
            context.conversation.append(img_message)
        except Exception as e:
            return f"Search error: {e}"
        