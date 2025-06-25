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
                description="The path to the file to be read",
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
                description="The path of the file to be written to",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file",
            ),
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
                description="The file to be run by the python interpreter",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


def process_agent_turn(
    client, messages_history, available_tools, system_instruction, verbose
):
    """
    Manages the agent's multi-step reasoning and tool execution
    until a final textual response is generated or a limit is reached.
    """
    for i in range(1, 20):  # The agent can make up to 19 internal calls/steps
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            config=types.GenerateContentConfig(
                tools=[available_tools],
                system_instruction=system_instruction,
            ),
            contents=messages_history,  # Use the history passed in
        )
        function_call_executed_this_turn = False

        for candidate in response.candidates:
            messages_history.append(candidate.content)  # Append LLM's thought/response
            for part in candidate.content.parts:
                if part.function_call:
                    function_call_executed_this_turn = True
                    print(f"Calling function: {part.function_call.name}")
                    function_call_result = call_function(
                        part.function_call, verbose  # Use verbose passed in
                    )
                    messages_history.append(function_call_result)  # Append tool output

        if not function_call_executed_this_turn:
            # If no function call was executed, the LLM provided a final text response
            if verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count} \n")
                print(
                    f"Response tokens: {response.usage_metadata.candidates_token_count}"
                )
            # The final textual response is in response.text
            return (
                response.text,
                messages_history,
            )  # Return the final text and updated history

        if verbose:
            # Token usage for internal LLM calls during tool execution
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count} \n")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    # If the loop finishes without a final text response (e.g., hit 20 calls limit)
    return (
        "Agent reached maximum internal steps without a final text response.",
        messages_history,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",
        help="User input prompt (required for one-shot mode, optional for interactive)",
    )
    parser.add_argument("--verbose", help="shows token usage", action="store_true")
    parser.add_argument(
        "--interactive", help="runs in interactive mode", action="store_true"
    )
    args = parser.parse_args()

    # Adjust the initial argument check to allow interactive mode without a prompt
    if not args.interactive and len(sys.argv) <= 1:
        print(
            "error: not enough arguments. Please provide a prompt or use --interactive mode."
        )
        sys.exit(1)

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Initialize messages list for conversation history
    messages = []

    if args.interactive:
        print("Entering interactive mode. Type 'quit' or 'exit' to end the session.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                print("Exiting interactive mode. Farewell!")
                break

            if not user_input.strip():  # Don't process empty input
                continue

            # Add user's message to the history
            messages.append(
                types.Content(role="user", parts=[types.Part(text=user_input)])
            )

            # Process the agent's turn with the current history
            final_response_text, _ = process_agent_turn(
                client,
                messages,  # Pass the accumulating messages history
                available_functions,
                system_prompt,
                args.verbose,
            )
            print(
                f"Boots: {final_response_text}"
            )  # Print the agent's final text response for this turn

    else:  # One-shot mode
        if not args.prompt:  # Ensure prompt is provided in one-shot mode
            print("error: 'prompt' argument is required for one-shot mode.")
            sys.exit(1)

        user_prompt = args.prompt
        # For one-shot mode, start with just the initial user prompt
        messages.append(
            types.Content(role="user", parts=[types.Part(text=user_prompt)])
        )
        # Call process_agent_turn once for the one-shot interaction
        final_response_text, _ = process_agent_turn(
            client, messages, available_functions, system_prompt, args.verbose
        )
        print(
            f"Boots: {final_response_text}"
        )  # Print the final response for the one-shot prompt


if __name__ == "__main__":
    main()
