import lldb
import os


class LldbWrapper:
    def __init__(self):
        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(False)
        self.target = None
        self.process = None
        self.initial_prompt = ""

    def get_initial_prompt(self) -> str:
        return self.initial_prompt

    def load_core(self, executable_path, coredump_path):
        if not os.path.exists(executable_path):
            print(f"Executable not found: {executable_path}")
            return False
        if not os.path.exists(coredump_path):
            print(f"Core dump not found: {coredump_path}")
            return False

        command = f'target create "{executable_path}" --core "{coredump_path}"'
        self.initial_prompt += "(lldb) " + command + "\n"
        res = lldb.SBCommandReturnObject()
        self.debugger.GetCommandInterpreter().HandleCommand(command, res)

        if res.Succeeded():
            self.initial_prompt += res.GetOutput() + "\n"
            self.target = self.debugger.GetSelectedTarget()
            self.process = self.target.GetProcess()
            return True
        else:
            error = res.GetError()
            self.initial_prompt += f"{error}\n"
            return False

    def run_command(self, command: str) -> str:
        if not self.target:
            raise Exception(f"Target not initialized")
        if not self.debugger:
            raise Exception(f"Debugger not initialized")

        res = lldb.SBCommandReturnObject()
        interpreter = self.debugger.GetCommandInterpreter()
        interpreter.HandleCommand(command, res)
        if res.Succeeded():
            return res.GetOutput()
        else:
            return res.GetError()

    def cleanup(self):
        if self.process:
            self.process.Kill()
        if self.debugger:
            lldb.SBDebugger.Destroy(self.debugger)

    def __del__(self):
        self.cleanup()
