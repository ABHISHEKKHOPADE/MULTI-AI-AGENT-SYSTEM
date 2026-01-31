import os
import logging
from datetime import datetime

Logs_DIR="logs"

os.makedirs(Logs_DIR,exist_ok=True) 
log_file=os.path.join(Logs_DIR,f"logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log") 
logging.basicConfig(filename=log_file,format='[%(asctime)s] %(levelname)s - %(message)s',level=logging.INFO)

def get_logger(name: str) -> logging.Logger:
    
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger