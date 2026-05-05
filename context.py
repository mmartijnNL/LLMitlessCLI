import os
from dataclasses import dataclass


@dataclass
class Context:
    conversation: list[dict[str, str]]
    assistant_name: str
    llm_model: str
    directory: str = os.path.expanduser("~")
    previous_directory: str = None
    conversation_file: str = "conversation.json"
    directory_file: str = "current_dir.json"
