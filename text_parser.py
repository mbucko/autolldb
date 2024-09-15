from typing import List, Tuple
import os


class TextParser:
    def parse_commands(self, text: str) -> Tuple[List[str], List[str]]:
        if not text:
            print("ERROR\n" + str(text))
            return [], []
        commands = []
        filenames = []
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("(lldb)"):
                command = line[len("(lldb)") :].strip()
                commands.append(command)
            elif line.startswith("(source)"):
                filepath = line[len("(source)") :].strip()
                filename = os.path.basename(filepath)
                filenames.append(filename)
        return commands, filenames
