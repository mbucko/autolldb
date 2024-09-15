import os


def search_file(source_dir, filename):
    for root, dirs, files in os.walk(source_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None


class FileSearcher:
    def __init__(self, source_dir):
        self.source_dir = source_dir

    def get_content(self, filename: str) -> str:
        full_path = search_file(self.source_dir, filename)

        if full_path:
            try:
                with open(full_path, "r") as file:
                    content = file.read()
            except Exception as e:
                content = f"Error reading file: {str(e)}"
        else:
            content = (
                f"Error: {filename} not found in {self.source_dir} or its subfolders."
            )
        return content
