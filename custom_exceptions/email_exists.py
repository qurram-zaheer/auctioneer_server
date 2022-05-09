class EmailAlreadyExistsException(Exception):
    def __init__(self):
        self.message = "Email already exists, please log in!"
        super().__init__(self.message)
