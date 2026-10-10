import sys


class CustomException(Exception):
    def __init__(self, message: str, _errors_detail: Exception = None):
        self.error_message = self.get_detailed_error_message(message)
        super().__init__(self.error_message)

    @staticmethod
    def get_detailed_error_message(message: str) -> str:
        _, _, exc_tb = sys.exc_info()
        if exc_tb is None:
            return message

        line_number = exc_tb.tb_lineno
        file_name = exc_tb.tb_frame.f_code.co_filename
        return (
            f"Error occurred in script: {file_name} at line number: {line_number}. "
            f"Error message: {message}"
        )

    def __str__(self):
        return self.error_message
