def file_contains(file: str, text: str) -> bool:
    with open(file, "r") as f:
        contents = f.read()
    return contents == text
