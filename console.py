import sys


COLOR_USER = "\033[94m"
COLOR_AI = "\033[92m"
COLOR_DEBUG = "\033[90m"
COLOR_THINKING = "\033[90m"
COLOR_ERROR = "\033[91m"
COLOR_RESET = "\033[0m"

def InitPrinting(config):
    global PRINT_DEBUG, PRINT_TERMINAL, PRINT_THINKING, LOAD_CONVERSATION
    PRINT_DEBUG = config.get("print_debug", False)
    PRINT_TERMINAL = config.get("print_terminal", False)
    PRINT_THINKING = config.get("print_thinking", False)
    LOAD_CONVERSATION = config.get("load_conversation", True)

def print_debug(label, msg):
    if PRINT_DEBUG:
        print(f"\n{COLOR_DEBUG}[{label}]\t{msg}{COLOR_RESET}\n")

def print_terminal(label, msg):
    if PRINT_TERMINAL:
        print(f"\n{COLOR_DEBUG}[{label}]\t{msg}{COLOR_RESET}\n")

def print_llm(msg):
    if PRINT_TERMINAL:
        print(f"\n{COLOR_AI}[LLM]\t{msg}{COLOR_RESET}\n")

def print_thinking(msg):
    if PRINT_THINKING:
        print(f"\n{COLOR_THINKING}[THINKING]\t{msg}{COLOR_RESET}\n")

def print_temp(msg):
    if PRINT_THINKING:
        print(f"{COLOR_DEBUG}...{COLOR_RESET}", end="", flush=True)
        sys.stdout.flush()
        print("\r", end="", flush=True)

def print_error(msg):
        print(f"\n{COLOR_ERROR}[ERROR]\t{msg}{COLOR_RESET}\n")

def input_user():
    return input(f"{COLOR_USER}[YOU]\t{COLOR_RESET}")