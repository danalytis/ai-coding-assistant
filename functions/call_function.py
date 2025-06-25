
from functions.get_file_content import *
from functions.get_files_info import *
from functions.run_python import *
from functions.write_file import *
from google.genai import types

working_dir = "./calculator"

function_mapping = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file
}

def call_function(function_call_part, verbose=False):

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")


    if function_call_part.name in function_mapping:

        args = function_call_part.args

        args["working_directory"] = working_dir

        function_name = function_mapping[function_call_part.name]

        function_result = function_name(**args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result},
                )
            ],
        )
    else:
        return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_call_part.name,
            response={"error": f"Unknown function: {function_call_part.name}"},
        )
    ],
)
