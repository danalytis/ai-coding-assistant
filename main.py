import os
import sys
import argparse

from functions.call_function import *
from dotenv import load_dotenv
from google import genai
from google.genai import types

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- When asked about "root" directory chose '.' as the value for directory argument instead
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the content of a file. 10000 characters Max",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description = "The path to the file to be read",
            )
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description = "The path of the file to be written to"
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description = "The content to be written to the file"
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description = "The file to be run by the python interpreter"
            ),
            "args" : types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING)
            )
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str, help="User input prompt")
    parser.add_argument("--verbose", help="shows token usage", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        print("error: not enough arguments")
        sys.exit(1)

    load_dotenv()
    user_prompt = args.prompt
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    for i in range(1, 20):

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
            contents=messages,
        )
        function_call_executed_this_turn = False

        for candidate in response.candidates:
            messages.append(candidate.content)
            for part in candidate.content.parts:
                if part.function_call:
                    function_call_executed_this_turn = True
                    print(f"Calling function: {part.function_call.name}")
                    function_call_result = call_function(part.function_call, args.verbose)
                    messages.append(function_call_result)

        if not function_call_executed_this_turn:
            print(response.text)
            break


        if args.verbose:
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count} \n")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()
