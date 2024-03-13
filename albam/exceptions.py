

class AlbamCheckFailure(Exception):

    def __init__(self, message, details, solution):
        super().__init__(message)
        self.message = message
        self.details = details
        self.solution = solution
