class Token:
    """A class to represent a description of a token of a language."""

    def __init__(self, name: str, regex: str):
        self.name = name
        self.regex = regex

    def __repr__(self) -> str:
        return f"Token<name={self.name},regex={self.regex}>"
