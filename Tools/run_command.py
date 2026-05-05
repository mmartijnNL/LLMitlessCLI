
import os
import subprocess
from typing import Any

from ..console import print_terminal

from .base_tool import BaseTool
from ..context import Context

class RunCommand(BaseTool):

    maxResults = 5

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": """Run a shell command on the local Linux machine. You will get the output. The user will not see the command or the output. 
                                Use cat to read and write files, ls to inspect directories, cd to change directories, and other standard Linux commands as needed.
                                You can sudo, the user will be prompted to enter their password if required.
                                You can use curl https://ipinfo.io/ip to get the public IP address of the machine.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to run.",
                        },
                    },
                    "required": ["command"],
                },
            },
        }
    

    @staticmethod
    def resolve_cd_target(raw_target: str, context: Context) -> str:
        target = raw_target.strip()

        if not target or target == "~":
            return os.path.expanduser("~")

        if target == "-":
            return context.previous_directory

        expanded_target = os.path.expanduser(target)
        if os.path.isabs(expanded_target):
            return os.path.normpath(expanded_target)

        return os.path.normpath(os.path.join(context.directory, expanded_target))

    
    @staticmethod    
    def handle_command(command: str, context: Context) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                cwd=context.directory,
            )
            output = (result.stdout or "") + (result.stderr or "")
            returncode = result.returncode
            return f"exit_code: {returncode}\n{output}"
        except Exception as exc:
            output = f"Command execution failed: {exc}"
            print_terminal("TERMINAL OUTPUT", output)
            return f"exit_code: 1\n{output}"

    @staticmethod
    def handle_command_cd(command: str, context: Context) -> str:
        _, _, raw_target = command.partition(" ")
        target_dir = RunCommand.resolve_cd_target(raw_target, context)
        if target_dir is None:
            return "cd: invalid target"

        if not os.path.isdir(target_dir):
            return f"cd: no such directory: {target_dir}"

        context.previous_directory = context.directory
        context.directory = target_dir
        lsResult = RunCommand.handle_command("ls", context)
        return  f"{target_dir} \n{lsResult}"


    def invoke(self, context: Context, command: str) -> str:

        if not isinstance(command, str) or not command.strip():
            return "exit_code: 1\nNo command provided."

        print_terminal("RUN", command)

        if command.startswith("cd") and (command == "cd" or command[2].isspace()):
            output = self.handle_command_cd(command, context)
        else:
            output = self.handle_command(command, context)

        if not output.strip():
            output = "[no output]"

        print_terminal("TERMINAL OUTPUT", output)
        context.conversation.append(
            {
                "role": "tool",
                "tool_name": self.name,
                "content": output,
            }
        )
        return output
        