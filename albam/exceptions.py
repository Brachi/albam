

class AlbamCheckFailure(Exception):

    def __init__(self, message, details, solution):
        super().__init__(message)
        self.message = message
        self.details = details
        self.solution = solution


class AlbamExportWarning(UserWarning):
    """A non-fatal, export-time notice (e.g. #375's Group ID check).

    Its own category, rather than plain UserWarning, so the operator that
    turns these into a self.report({'WARNING'}, ...) can filter for exactly
    this and not surface an unrelated library's own warnings.warn() call
    (numpy, PIL, etc.) as if it were an export-correctness notice.
    """
