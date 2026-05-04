import subprocess
import ollama
import json
import os
import platform
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "configuration.json"), "r") as _cfg_file:
    _config = json.load(_cfg_file)

LLM_MODEL = _config["model"]
ASSISTANT_NAME = _config["name"]

PRINT_DEBUG = _config.get("print_debug", False)
PRINT_TERMINAL = _config.get("print_terminal", False)
PRINT_THINKING = _config.get("print_thinking", False)

CONVO_FILE = "conversation.json"
CURRENT_DIR = os.path.expanduser("~")
PREVIOUS_DIR = None

COLOR_USER = "\033[94m"
COLOR_AI = "\033[92m"
COLOR_DEBUG = "\033[90m"
COLOR_THINKING = "\033[90m"
COLOR_ERROR = "\033[91m"
COLOR_RESET = "\033[0m"


def print_debug(label, msg):
    if PRINT_DEBUG:
        print(f"\n{COLOR_DEBUG}[{label}]\t{msg}{COLOR_RESET}\n")
def print_terminal(label, msg):
    if PRINT_TERMINAL:
        print(f"\n{COLOR_DEBUG}[{label}]\t{msg}{COLOR_RESET}\n")
def print_thinking(msg):
    if PRINT_THINKING:
        print(f"\n{COLOR_THINKING}[THINKING]\t{msg}{COLOR_RESET}\n")
def print_error(msg):
        print(f"\n{COLOR_ERROR}[ERROR]\t{msg}{COLOR_RESET}\n")

def save_conversation():
    """Save conversation to file on exit"""
    try:
        with open(CONVO_FILE, 'w') as f:
            json.dump(conversation, f, indent=2)
        print_debug("SAVE", f"Conversation saved to {CONVO_FILE}")
    except Exception as e:
        print_error(f"SAVE ERROR: {str(e)}")
def load_conversation():
    """Load conversation from file on startup"""
    if not os.path.exists(CONVO_FILE):
        print_debug("LOAD", f"No saved conversation found at {CONVO_FILE}")
        return False
    try:
        with open(CONVO_FILE, 'r') as f:
            global conversation
            conversation = json.load(f)
        print_debug("LOAD", f"Loaded conversation from {CONVO_FILE}")
        return True
    except Exception as e:
        print_error(f"LOAD ERROR: {str(e)}")
        return False
def save_dir():
    """Save current directory to file on exit"""
    try:
        with open("current_dir.json", 'w') as f:
            json.dump({"current_dir": CURRENT_DIR}, f, indent=2)
        print_debug("SAVE", f"Current directory saved to current_dir.json")
    except Exception as e:
        print_error(f"SAVE ERROR: {str(e)}")
def load_dir():
    """Load current directory from file on startup"""
    if not os.path.exists("current_dir.json"):
        print_debug("LOAD", f"No saved directory found at current_dir.json")
        return False
    try:
        with open("current_dir.json", 'r') as f:
            global CURRENT_DIR
            data = json.load(f)
            CURRENT_DIR = data.get("current_dir", os.getcwd())
        print_debug("LOAD", f"Loaded current directory from current_dir.json")
        return True
    except Exception as e:
        print_error(f"LOAD ERROR: {str(e)}")
        return False

def set_working_dir(message):
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    return message

def format_message(message):
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    return message

def resolve_cd_target(raw_target: str) -> str:
    target = raw_target.strip()

    if not target or target == "~":
        return os.path.expanduser("~")

    if target == "-":
        return PREVIOUS_DIR

    expanded_target = os.path.expanduser(target)
    if os.path.isabs(expanded_target):
        return os.path.normpath(expanded_target)

    return os.path.normpath(os.path.join(CURRENT_DIR, expanded_target))

def handle_command(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            cwd=CURRENT_DIR,
        )
        output = (result.stdout or "") + (result.stderr or "")
        returncode = result.returncode
        return f"exit_code: {returncode}\n{output}"
    except Exception as exc:
        output = f"Command execution failed: {exc}"
        print_terminal("TERMINAL OUTPUT", output)
        return f"exit_code: 1\n{output}"

def handle_command_cd(command: str) -> str:
    _, _, raw_target = command.partition(" ")
    target_dir = resolve_cd_target(raw_target)
    if target_dir is None:
        return "cd: invalid target"

    if not os.path.isdir(target_dir):
        return f"cd: no such directory: {target_dir}"

    global PREVIOUS_DIR, CURRENT_DIR
    PREVIOUS_DIR = CURRENT_DIR
    CURRENT_DIR = target_dir
    save_dir()
    lsResult = handle_command("ls")
    return  f"{target_dir} \n{lsResult}"

def tool_run_command(command: str) -> str:
    """Run a shell command on the local Linux machine.

    Args:
      command: Shell command to execute. You will get the output. The user will not see the command or the output. 
      Use cat to read and write files, ls to inspect directories, cd to change directories, and other standard Linux commands as needed.
      You can sudo, the user will be prompted to enter their password if required.
      You can use curl https://ipinfo.io/ip to get the public IP address of the machine.

    Returns:
      str: Combined execution result including exit code and stdout/stderr.
    """
    if not isinstance(command, str) or not command.strip():
        return "exit_code: 1\nNo command provided."

    print_terminal("RUN", command)

    if command.startswith("cd") and (command == "cd" or command[2].isspace()):
        output = handle_command_cd(command)
    else:
        output = handle_command(command)

    if not output.strip():
        output = "[no output]"

    print_terminal("TERMINAL OUTPUT", output)
    return output

def tool_web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
      query: Search query string.
      max_results: Maximum number of results to return (default 5).

    Returns:
      str: Search results with titles, URLs, and snippets.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r.get('title', 'No title')}\n   URL: {r.get('href', '')}\n   {r.get('body', '')}")
        return "\n\n".join(output)
    except ImportError:
        return "Error: ddgs not installed. Run: pip install ddgs"
    except Exception as e:
        return f"Search error: {e}"

def tool_fetch_page(url: str) -> str:
    """Fetch and return the text content of a web page.

    Args:
      url: The URL to fetch.

    Returns:
      str: The text content of the page (truncated to 8000 chars if too long).
    """
    try:
        import requests
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
        return content if content else "[No readable content found]"
    except ImportError:
        return "Error: requests not installed. Run: pip install requests"
    except Exception as e:
        return f"Fetch error: {e}"

TOOLS = [tool_run_command, tool_web_search, tool_fetch_page]

def os_details():
    desktopSession = subprocess.run("echo $DESKTOP_SESSION", shell=True, text=True, capture_output=True)
    desktopSessionCurrent = subprocess.run("echo $XDG_CURRENT_DESKTOP", shell=True, text=True, capture_output=True)
    return f"{os.name} {platform.system()} {platform.release()} {desktopSession.stdout.strip()} {desktopSessionCurrent.stdout.strip()}"

system = {
    "role": "system",
    "content": f"""
    You are {ASSISTANT_NAME}, a personal assistant.
    You are running locally on the user's machine. Meaning you can access everything on the users computer. 
    
    Use the provided tools to interact with the local machine and the web to help the user with their tasks.
    You can find out things about the user by using your tools.
    Your LLM model is {LLM_MODEL}, running through OLLAMA.
    Your source code can be found at {dir_path}
    Computer details: {os_details()}.
    Please be consise in your responses.
"""
}

conversation = [system]

def run_assistant_turn():
    while True:
        print_debug("TO LLM", conversation[-1]["content"] if conversation else "")
        print(f"{COLOR_DEBUG}...{COLOR_RESET}", end="", flush=True)

        sys.stdout.flush()

        response = ollama.chat(model=LLM_MODEL, messages=conversation, tools=TOOLS)

        print("\r", end="", flush=True)

        message = response.message
        print_debug("FROM LLM", format_message(message))

        tool_calls = list(message.tool_calls or [])

        assistant_message = {"role": "assistant"}
        if message.content is not None:
            assistant_message["content"] = message.content
        if tool_calls:
            assistant_message["tool_calls"] = [tool_call.model_dump() for tool_call in tool_calls]
        if message.thinking:
            print_thinking(message.thinking)
            assistant_message["thinking"] = message.thinking
        conversation.append(assistant_message)
        save_conversation()

        if message.content:
            print(f"{COLOR_AI}[AI]{COLOR_RESET}\t{message.content.strip()}\n", end="", flush=True)

        if tool_calls == [] and (not message.thinking or (message.thinking and message.thinking)):
            return        

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = dict(tool_call.function.arguments)

            if tool_name == "tool_run_command":
                tool_output = tool_run_command(**tool_args)
            elif tool_name == "tool_web_search":
                tool_output = tool_web_search(**tool_args)
            elif tool_name == "tool_fetch_page":
                tool_output = tool_fetch_page(**tool_args)
            else:
                tool_output = f"exit_code: 1\nUnknown tool: {tool_name}"

            conversation.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": tool_output,
                }
            )

if __name__ == "__main__":
    # Load existing conversation on startup
    if load_conversation():
        print("Loaded previous conversation. Type 'reset' to start fresh.")
        load_dir()
    else:
        print(f"{COLOR_AI}[NEW CONVERSATION]{COLOR_RESET}")
        

    while True:
        user_input = input(f"{COLOR_USER}[YOU] \t{COLOR_RESET}")

        if user_input.lower() == "reset" or user_input.lower() == "r":
            conversation = [system]
            CURRENT_DIR = os.path.expanduser("~")
            PREVIOUS_DIR = None
            print(f"{COLOR_AI}[NEW CONVERSATION]{COLOR_RESET}")
            save_conversation()
            save_dir()
            continue
        elif user_input.lower() == "debug on":
            PRINT_DEBUG = True
            print(f"{COLOR_DEBUG}Debug = {PRINT_DEBUG}{COLOR_RESET}")
            continue
        elif user_input.lower() == "debug off":
            PRINT_DEBUG = False
            print(f"{COLOR_DEBUG}Debug = {PRINT_DEBUG}{COLOR_RESET}")
            continue
        elif user_input.lower() == "terminal on":
            PRINT_TERMINAL = True
            print(f"{COLOR_DEBUG}Terminal = {PRINT_TERMINAL}{COLOR_RESET}")
            continue
        elif user_input.lower() == "terminal off":
            PRINT_TERMINAL = False
            print(f"{COLOR_DEBUG}Terminal = {PRINT_TERMINAL}{COLOR_RESET}")
            continue
        elif user_input.lower() == "thinking on":
            PRINT_THINKING = True
            print(f"{COLOR_DEBUG}Thinking = {PRINT_THINKING}{COLOR_RESET}")
            continue
        elif user_input.lower() == "thinking off":
            PRINT_THINKING = False
            print(f"{COLOR_DEBUG}Thinking = {PRINT_THINKING}{COLOR_RESET}")
            continue
        elif user_input.lower() == "help" or user_input.lower() == "h":
            print(
                """Commands:
                (r)eset - Clear conversation history 
                debug on/off - Enable/Disable debug output
                terminal on/off - Enable/Disable debug output
                thinking on/off - Enable/Disable thinking messages
                """)
            continue

        conversation.append({"role": "user", "content": user_input})

        try:
            run_assistant_turn()
        except Exception as exc:
            print_debug("EXCEPTION", str(exc))
            print_error(str(exc))
            conversation.append(
                {
                    "role": "system",
                    "content": f"[error]\n{exc}",
                }
            )