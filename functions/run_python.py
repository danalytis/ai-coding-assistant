import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    if args is None:
        args = []
    abs_directory = os.path.normpath(os.path.abspath(os.path.join(working_directory, file_path)))
    abs_working_directory = os.path.normpath(os.path.abspath(working_directory))
    if os.path.commonpath([abs_working_directory, abs_directory]) != abs_working_directory:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_directory):
        return f'Error: File "{file_path}" not found.'
    file_split = os.path.splitext(file_path)
    if file_split[1] != '.py':
        return f'Error: "{file_path}" is not a Python file.'

    try:
        command = ["python3", file_path] + args
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            timeout=30

        )
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()
        returncode = result.returncode

        if not stdout.strip() and not stderr.strip():
            return "No output produced."
        output = f'STDOUT:{stdout}\nSTDERR:{stderr}'
        if returncode != 0:
            output += f'\nProcess exited with code {returncode}'
        return output
    except Exception as e:
        return f"Error: executing Python file: {e}"
