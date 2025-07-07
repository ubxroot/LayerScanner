# utils/logger.py

import logging
from rich.logging import RichHandler # For better console logging with Rich

def setup_logger():
    """
    Sets up a basic logger for the LayerScanner tool.
    Logs to console with RichHandler and to a file.
    """
    logger = logging.getLogger("LayerScanner")
    logger.setLevel(logging.INFO) # Set default logging level

    # Prevent adding multiple handlers if already configured
    if not logger.handlers:
        # RichHandler for console output
        console_handler = RichHandler(
            show_time=False, # Time handled by rich.print in main
            show_level=True,
            show_path=False,
            enable_link_path=False,
            markup=True
        )
        logger.addHandler(console_handler)

        # File handler for detailed logs
        file_handler = logging.FileHandler("layerscanner.log")
        file_handler.setLevel(logging.DEBUG) # Log all debug messages to file
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

