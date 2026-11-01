class RegexSyntaxError(ValueError):
    def __init__(
        self, message: str, pattern: str, position: int, *args: object
    ) -> None:
        super().__init__(message, *args)
        self.message = message
        self.pattern = pattern
        self.position = position
