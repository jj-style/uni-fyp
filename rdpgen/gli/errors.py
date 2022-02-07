class MissingTypeError(Exception):
    def __init__(self):
        super().__init__("type must be provided")
