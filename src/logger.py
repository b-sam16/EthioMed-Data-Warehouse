import logging
import os

# Ensure logs folder exists
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

def get_logger(module_name: str):
    """
    Creates and returns a logger for a given module, ensuring that each module's logs 
    are written to a separate file under the `logs` directory.
    """
    logger = logging.getLogger(module_name)
    if not logger.hasHandlers():
        # Create a file handler for each module's log
        file_handler = logging.FileHandler(os.path.join(log_dir, f"{module_name}.log"))
        file_handler.setLevel(logging.INFO)
        
        # Create a console handler for live output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and set it for the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
    return logger
