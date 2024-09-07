class GenericError(Exception):
    def __init__(self, code: int = -1, message : str = "Something went wrong") -> None:
        self.code = code
        self.message = message
        
class InvalidInputError(GenericError):
    def __init__(self, message: str = "Invalid Input") -> None:
        super().__init__(2, message)
        
class InvalidCredentialsError(GenericError):
    def __init__(self, message: str = "Invalid username or password") -> None:
        super().__init__(3, message)
        
class ServiceDoesNotExistError(GenericError):
    def __init__(self, message: str = "This service does not exist") -> None:
        super().__init__(4, message)