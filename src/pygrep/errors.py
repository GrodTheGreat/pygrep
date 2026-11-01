class UsageError(Exception):
    def __init__(self, message: str | None = None, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message
