import sys  ## for printing exception info

class CustomException(Exception):

    
    def __init__(self,message:str,errors_detail:Exception=None):
       
        self.error_message=self.get_detailed_error_message(message,errors_detail)
        super().__init__(self.error_message) 

    @staticmethod 
    def get_detailed_error_message(message:str,errors_detail:Exception=None)->str:

            _,_,exc_tb=sys.exc_info()  
            if exc_tb is None:
               return message
            line_number=exc_tb.tb_lineno  
            file_name=exc_tb.tb_frame.f_code.co_filename  
            error_message=f"Error occurred in script: {file_name} at line number: {line_number} . Error message: {message}"
            return error_message
        
    def __str__(self): 
            return self.error_message 