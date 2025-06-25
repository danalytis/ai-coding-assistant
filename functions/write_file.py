import os

def write_file(working_directory, file_path, content):

    abs_directory = os.path.normpath(os.path.abspath(os.path.join(working_directory, file_path)))
    abs_working_directory = os.path.normpath(os.path.abspath(working_directory))
    if os.path.commonpath([abs_working_directory, abs_directory]) != abs_working_directory:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        if not os.path.exists(os.path.dirname(abs_directory)):
            os.makedirs(os.path.dirname(abs_directory))
        with open(abs_directory, "w") as f:
            f.write(content)
        return f'Succesfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"
