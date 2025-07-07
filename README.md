## LayerScanner - Onion Web Scanning Tool
![LayerScanner Logo/Banner (Optional - you can add an image here)](https://img.shields.io/badge/Blue%20Team-Security-blue?style=for-the-badge&logo=shield)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

LayerScanner is a specialized command-line tool designed for gathering information and performing light reconnaissance on Tor (.onion) websites. It helps security researchers, ethical hackers, and blue teams understand the public-facing aspects and potential configurations of hidden services by routing all traffic through the Tor network.

## ✨ Features
* Tor Network Integration: All web requests are automatically routed through a local Tor SOCKS5 proxy (127.0.0.1:9050 by default), enabling seamless access to .onion addresses.
* Basic Site Information Gathering: Fetches and displays fundamental details about the target site, including HTTP status codes, page titles, and server headers.
* robots.txt Analysis: Automatically retrieves and parses the robots.txt file to identify paths that the site owner has requested not be indexed, which can sometimes hint at sensitive areas.
* Common Path Scanning: Checks for a predefined list of commonly exposed directories and files (e.g., /admin/, /.env, /backup.zip) that might indicate misconfigurations or unintentional information disclosure.
* Internal Link Extraction & Crawling: Extracts other .onion links found within the same hidden service and can recursively crawl them up to a specified depth, expanding the discovery scope.
* Structured & Readable Output: Presents scan results in a clear, color-coded table format directly in the terminal using rich, making findings easy to digest.
* JSON Export: Supports exporting all gathered information and findings in a machine-readable JSON format for further analysis or integration with other tools.
* Configurable Settings: Allows customization of Tor proxy settings, scan timeouts, and the list of common paths to check via a user-editable configuration file.
* Detailed Logging: Maintains a layerscanner.log file for comprehensive logging of scan activities, errors, and debugging information.

## 🚀 Installation
# Clone the repository:
```
git clone https://github.com/ubxroot/LayerScanner.git
cd LayerScanner
```

# Install dependencies:
LayerScanner relies on several Python packages. Ensure you have pip installed, then run:
```
sudo pip install -r requirements.txt
```
(This command will install typer, rich, requests[socks], pyfiglet, and beautifulsoup4.)

# Make the main script executable:
```
chmod +x layerscanner.py
```
# Ensure Tor Service is Running:
LayerScanner requires the Tor service to be running on your system to route traffic. On Kali Linux, you can usually start it with:
```
sudo service tor start
```
You can check its status with sudo service tor status.

## 💡 Usage
Basic Scan:
To perform a basic scan of an .onion URL with a default crawl depth of 1:

./layerscanner.py scan http://example.onion/

## Scan with Increased Depth and Verbose Output:
# To crawl internal links up to 2 hops deep and see detailed logging:

./layerscanner.py scan http://example.onion/ --depth 2 --verbose

# Output Results as JSON:
To get the scan results in JSON format, useful for scripting or integration:

./layerscanner.py scan http://example.onion/ --output json

## Customizing Configuration:
The first time you run layerscanner.py, a default configuration file will be created at ~/.layerscanner_config.json. You can edit this file to customize Tor proxy settings, scan timeouts, or add/modify common paths to check:

nano ~/.layerscanner_config.json

## 📊 Example Output (Human Readable Table)
LayerScanner: Scanning http://example.onion/ (Depth: 1)

  [+] Initial connection successful. HTTP Status: 200
  [dim]  Checking robots.txt at http://example.onion/robots.txt...[/dim]
  [dim]  No disallowed paths found in robots.txt.[/dim]
  [dim]  Checking common path: http://example.onion/admin/...[/dim]
  [dim]  Path /admin/ not found (Status: 404).[/dim]
  [dim]  Checking common path: http://example.onion/robots.txt...[/dim]
  [dim]  Path /robots.txt not found (Status: 404).[/dim]
  [dim]  Checking common path: http://example.onion/sitemap.xml...[/dim]
  [dim]  Path /sitemap.xml not found (Status: 404).[/dim]

## Development & Contributions
LayerScanner is an open-source project, and contributions are highly welcome! If you find bugs, have feature requests, or want to contribute code, please feel free to:

## Open an issue

Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
