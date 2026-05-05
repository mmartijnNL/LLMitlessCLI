import sys

class Console():
    COLOR_USER = "\033[94m"
    COLOR_AI = "\033[92m"
    COLOR_DEBUG = "\033[90m"
    COLOR_THINKING = "\033[90m"
    COLOR_ERROR = "\033[91m"
    COLOR_RESET = "\033[0m"
    _temp_active = False

    @staticmethod
    def InitPrinting(config):
        global PRINT_DEBUG, PRINT_TERMINAL, PRINT_THINKING, LOAD_CONVERSATION
        PRINT_DEBUG = config.get("print_debug", False)
        PRINT_TERMINAL = config.get("print_terminal", False)
        PRINT_THINKING = config.get("print_thinking", False)
        LOAD_CONVERSATION = config.get("load_conversation", True)

    @staticmethod
    def set_print_debug(value: bool):
        global PRINT_DEBUG
        PRINT_DEBUG = value
        print(f"Debug = {PRINT_DEBUG}")

    @staticmethod
    def set_print_terminal(value: bool):
        global PRINT_TERMINAL
        PRINT_TERMINAL = value
        print(f"Terminal = {PRINT_TERMINAL}")

    @staticmethod
    def set_print_thinking(value: bool):
        global PRINT_THINKING
        PRINT_THINKING = value
        print(f"Thinking = {PRINT_THINKING}")

    @staticmethod
    def set_load_conversation(value: bool):
        global LOAD_CONVERSATION
        LOAD_CONVERSATION = value
        print(f"Load Conversation = {LOAD_CONVERSATION}")

    @staticmethod
    def print_debug(label, msg):
        if PRINT_DEBUG:
            print(f"{Console.COLOR_DEBUG}[{label}]\t{msg}{Console.COLOR_RESET}")

    @staticmethod
    def print_terminal(label, msg):
        if PRINT_TERMINAL:
            print(f"{Console.COLOR_DEBUG}[{label}]\t{msg}{Console.COLOR_RESET}")

    @staticmethod
    def print_thinking(msg):
        if PRINT_THINKING:
            print(f"{Console.COLOR_THINKING}[THINKING]\t{msg}{Console.COLOR_RESET}")

    @staticmethod
    def print_temp(msg = "..."):
        print(f"{Console.COLOR_DEBUG}{msg}{Console.COLOR_RESET}", end="", flush=True)
        Console._temp_active = True

    @staticmethod
    def _clear_temp():
        if Console._temp_active:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()
            Console._temp_active = False

    @staticmethod
    def print_llm(msg):
        Console._clear_temp()
        print(f"{Console.COLOR_AI}[LLM]\t{Console.COLOR_RESET}{msg}")

    @staticmethod
    def input_user():
        return input(f"{Console.COLOR_USER}[YOU]\t{Console.COLOR_RESET}")

    @staticmethod
    def print_error(msg):
        print(f"{Console.COLOR_ERROR}[ERROR]\t{msg}{Console.COLOR_RESET}\n")


# Module-level aliases
InitPrinting = Console.InitPrinting
print_debug = Console.print_debug
print_terminal = Console.print_terminal
print_llm = Console.print_llm
print_thinking = Console.print_thinking
print_temp = Console.print_temp
print_error = Console.print_error
input_user = Console.input_user