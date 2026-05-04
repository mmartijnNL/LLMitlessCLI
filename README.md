# LLMitlessCLI

Stop pasting commands from ChatGPT into the terminal like a chump. These systems should already be talking to each other.

LLMitlessCLI connects an LLM (via Ollama) directly to your shell, turning requests into execution instead of instructions.

No copy/paste loop. No manual step in between. No need to learn how the terminal works.

## what it is
An agentic layer on top of Ollama that can:
- run shell commands
- react to command output (auto-fix issues and continue execution)
- search the web and feed results directly into terminal actions

## requirements
- Linux (probably) 
- Ollama running locally

## warning
LLMitlessCLI executes LLM-generated commands directly on your system without confirmation, including destructive ones.

It is partly a joke. 