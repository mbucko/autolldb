from lldb_wrapper import LldbWrapper
from llm_wrapper import LlmWrapper
from text_parser import TextParser
from file_searcher import FileSearcher
import argparse

# import debugpy


# Ollama API
# https://www.youtube.com/watch?v=d0o89z134CQ&ab_channel=TechWithTim


system_prompt = """
You are a bot trying to debug a corefile using lldb.
Your mission is to do the following:
    * Gather information about the process, memory and source files and why it's failing.
    * Write summary of the bug.
    * Create a diff for fixing it.

You will have the following API at your disposal:
(lldb) <your lldb command>
(source) <your source file>
(SUMMARY) <you write the summary>
(DIFF) <your diff that fixes the bug>

Make sure you type the commands exactly as it is above and only when you want to invoke them!!!
For example:
(lldb) bt
(source) MyFile.cpp
(lldb) var

You read and analyse the data I give you, then use chain of thought reasoning about it and then you MUST output one of the following:
* one or more of (source)/(lldb) commands
* (SUMMARY) followed by (DIFF)

When I say chain of thought I mean that you explain its reasoning briefly before issuing commands or providing summaries. You must keep the explaination VERY minimal and don't state the commands unless you're actully trying to invoke them.

The process should look like this:
Analyse the data I give you, you chain of thought reasoning to determine whether you have enough data to print (SUMMARY) and (DIFFF). If so print it. If not use chain of thought reasoning to determine what commands to issue in order to get more data about the bug that might be useful to get closer to finding the bug.

Hint:
Use commands such as "bt" for backtrace to figure out where it has failed.
Look up any relevant source files using (source) command.
If needed change the fram using (lldb) f <number>
Examine variabled using (lldb) var <variable name>
Dig deep until you find the underlying issue in the code. Assume tests are correct!!!
"""

initial_prompt = """
Here is the starting state of our process:
"""

executable_path = "/Users/mbucko/repos/proactor/build/Debug/tests"
coredump_path = "/Users/mbucko/repos/autolldb/proactor.core"
source_dir = "/Users/mbucko/repos/proactor/"


def truncate_content(content, max_lines=3):
    lines = content.split("\n")
    if len(lines) > max_lines:
        truncated = "\n".join(lines[:max_lines]) + "\n..."
    else:
        truncated = content
    return truncated


def main():
    parser = argparse.ArgumentParser(description="Debug a corefile using lldb and LLM.")
    parser.add_argument(
        "-a", "--api-key", type=str, help="API key for the LLM service", required=True
    )
    parser.add_argument(
        "-e", "--executable", type=str, help="Path to the executable", required=True
    )
    parser.add_argument(
        "-c", "--coredump", type=str, help="Path to the coredump file", required=True
    )
    parser.add_argument(
        "-s",
        "--source-dir",
        type=str,
        help="Path to the source directory",
        required=True,
    )
    args = parser.parse_args()

    llm_wrapper = LlmWrapper(system_prompt, args.api_key)
    text_parser = TextParser()
    lldb_wrapper = LldbWrapper()
    file_searcher = FileSearcher(args.source_dir)

    if not lldb_wrapper.load_core(args.executable, args.coredump):
        raise Exception(
            f"Failed to load core dump. Please check the following paths:\n"
            f"Executable: {args.executable}\n"
            f"Core dump: {args.coredump}"
        )
    prompt = initial_prompt + lldb_wrapper.get_initial_prompt()

    for i in range(10):
        ok, llm_output = llm_wrapper.ask(prompt)
        if not ok:
            print("Llm failed, Stopping. " + llm_output)
            break
        summary = llm_output
        commands, filenames = text_parser.parse_commands(llm_output)
        prompt = ""
        for command in commands:
            lldb_output = lldb_wrapper.run_command(command)
            prompt += command + "\n" + lldb_output + "\n"

        for filename in filenames:
            content = file_searcher.get_content(filename)
            prompt += "filename: " + filename + ":\n" + content + "\n\n"

        if len(prompt) == 0:
            prompt = "No commands were provided! Please specify either (lldb) or (source) commands."

        if "(SUMMARY)" in llm_output:
            print("Stopping because SUMMARY was issued")
            break

    try:
        file_path = "autolldb_llm_log.log"
        with open(file_path, "w") as file:
            file.write(llm_wrapper.get_conversation_history())
        print(f"Llm log has been successfully saved to {file_path}")
    except IOError as e:
        print(f"Error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
