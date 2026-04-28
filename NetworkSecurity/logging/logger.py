import logging 
import os
import sys
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%m_%d_%y_%H_%M_%S')}.log"

logs_folder_path = os.path.join(os.getcwd(), "logs")

os.makedirs(logs_folder_path, exist_ok=True)

log_file_path = os.path.join(logs_folder_path, LOG_FILE)

logging.basicConfig(
    filename=log_file_path,
    format= "%(asctime)s %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO
)

if __name__ == "__main__":
    logging.info("Logging has started")