import os


def get_files_info(working_directory, directory=None):
    if directory is None:
        directory = "."
    abs_directory = os.path.normpath(os.path.abspath(os.path.join(working_directory, directory)))
    abs_working_directory = os.path.normpath(os.path.abspath(working_directory))
    if os.path.commonpath([abs_working_directory, abs_directory]) != abs_working_directory:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(abs_directory):
        return f'Error: "{directory}" is not a directory'

    # - README.md: file_size=1032 bytes, is_dir=False
    # - src: file_size=128 bytes, is_dir=True
    # - package.json: file_size=1234 bytes, is_dir=False
    contents = os.listdir(abs_directory)
    result = []
    for item in contents:
        item_path = os.path.join(abs_directory, item)
        result.append(
            f"- {item}: file_size={ os.path.getsize(item_path) }, is_dir={os.path.isdir(item_path)} \n"
        )
    return "".join(result)
