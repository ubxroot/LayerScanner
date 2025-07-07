# utils/config.py

import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger("LayerScanner")

# Path to the custom configuration file in the user's home directory.
CONFIG_FILE_PATH = Path.home() / ".layerscanner_config.json"

def load_config() -> Dict[str, Any]:
    """
    Loads configuration from a JSON file in the user's home directory.
    If the file doesn't exist, it creates a default one.
    """
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_FILE_PATH}")
                return config
        except json.JSONDecodeError:
            logger.error(f"Error parsing config file {CONFIG_FILE_PATH}. Using default config.", exc_info=True)
            return _get_default_config()
    else:
        default_config = _get_default_config()
        try:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file at {CONFIG_FILE_PATH}")
        except IOError:
            logger.error(f"Could not write default config file to {CONFIG_FILE_PATH}. Using default config.", exc_info=True)
        return default_config

def _get_default_config() -> Dict[str, Any]:
    """Returns a default configuration dictionary for LayerScanner."""
    return {
        "tor_proxy": {
            "http": "socks5h://127.0.0.1:9050", # SOCKS5h for hostname resolution through proxy
            "https": "socks5h://127.0.0.1:9050"
        },
        "scan_timeout": 15, # Timeout for HTTP requests
        "common_paths": [
            "/admin/", "/login.php", "/panel/", "/dashboard/", "/config.php",
            "/.env", "/phpinfo.php", "/test.php", "/backup.zip", "/sitemap.xml",
            "/robots.txt", "/.git/config", "/.svn/entries", "/README.md",
            "/index.php.bak", "/.htaccess", "/wp-admin/", "/wp-login.php"
        ]
    }

