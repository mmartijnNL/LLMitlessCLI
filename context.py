
from dataclasses import dataclass


@dataclass
class Context:
    conversation: list[dict[str, str]]
    assistant_name: str
    llm_model: str
    directory: str
    previous_directory: str
    conversation_file: str = "conversation.json"
    directory_file: str = "current_dir.json"
