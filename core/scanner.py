# core/scanner.py

import requests
from urllib.parse import urlparse, urljoin
from collections import deque
from typing import List, Dict, Any, Optional
import logging

from rich.console import Console
from rich.text import Text
from rich.markup import escape

from utils.config import load_config
from core.parser import get_page_title, extract_onion_links

logger = logging.getLogger("LayerScanner")

def _get_tor_session(config: Dict[str, Any]) -> requests.Session:
    """Configures and returns a requests session to route through Tor."""
    session = requests.session()
    tor_proxy = config.get("tor_proxy", {})
    session.proxies = {
        'http': tor_proxy.get('http', 'socks5h://127.0.0.1:9050'),
        'https': tor_proxy.get('https', 'socks5h://127.0.0.1:9050')
    }
    return session

def _fetch_url_tor(session: requests.Session, url: str, timeout: int, console: Console) -> Optional[requests.Response]:
    """Fetches a URL through the Tor session."""
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.exceptions.ConnectionError as e:
        console.print(f"[red]  [!] Connection error to {url}: Tor service not running or unreachable. Ensure Tor is active.[/red]")
        logger.error(f"Connection error to {url}: {e}")
        return None
    except requests.exceptions.Timeout:
        console.print(f"[yellow]  [!] Timeout fetching {url}.[/yellow]")
        logger.warning(f"Timeout fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[red]  [!] Request error fetching {url}: {escape(str(e))}[/red]")
        logger.error(f"Request error fetching {url}: {e}")
        return None
    except Exception as e:
        console.print(f"[red]  [!] Unexpected error fetching {url}: {escape(str(e))}[/red]")
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None

def scan_onion_site(
    onion_url: str,
    depth: int,
    logger: logging.Logger,
    config: Dict[str, Any],
    console: Console
) -> List[Dict[str, Any]]:
    """
    Scans an onion site, performing basic information gathering and crawling.
    """
    findings = []
    visited_urls = set()
    queue = deque([(onion_url.rstrip('/'), 0)]) # (url, current_depth)
    
    session = _get_tor_session(config)
    scan_timeout = config.get("scan_timeout", 15)
    common_paths = config.get("common_paths", [])

    console.print(f"[bold cyan]Starting scan on {onion_url} (Max Depth: {depth})...[/bold cyan]")
    logger.info(f"Starting scan on {onion_url} with max_depth={depth}")

    # Initial check to ensure the base URL is reachable via Tor
    console.print("[dim]  Testing Tor connectivity and initial URL...[/dim]")
    initial_response = _fetch_url_tor(session, onion_url, scan_timeout, console)
    if not initial_response:
        console.print("[bold red]  [!] Initial connection to onion site failed. Cannot proceed with scan.[/bold red]")
        logger.error(f"Initial connection to {onion_url} failed.")
        return []
    else:
        console.print(f"[green]  [+] Initial connection successful. HTTP Status: {initial_response.status_code}[/green]")
        logger.info(f"Initial connection to {onion_url} successful. Status: {initial_response.status_code}")
        
        # Add initial site details as a finding
        initial_title = get_page_title(initial_response.text)
        findings.append({
            "type": "Site Info",
            "url": onion_url,
            "status_code": initial_response.status_code,
            "title": initial_title if initial_title else "N/A",
            "server_header": initial_response.headers.get('Server', 'N/A'),
            "description": "Initial site information."
        })
        visited_urls.add(onion_url.rstrip('/'))

    # --- Main Crawling Loop ---
    while queue:
        current_url, current_depth = queue.popleft()

        if current_depth > depth:
            continue
        
        if current_url not in visited_urls:
            visited_urls.add(current_url)
            console.print(f"[dim]  Crawling: {current_url} (Depth: {current_depth})[/dim]")
            logger.info(f"Crawling: {current_url} (Depth: {current_depth})")

            response = _fetch_url_tor(session, current_url, scan_timeout, console)
            if response:
                # Add current page details if not already added by initial check
                if current_url != onion_url:
                    page_title = get_page_title(response.text)
                    findings.append({
                        "type": "Page Info",
                        "url": current_url,
                        "status_code": response.status_code,
                        "title": page_title if page_title else "N/A",
                        "server_header": response.headers.get('Server', 'N/A'),
                        "description": f"Page details at depth {current_depth}."
                    })

                # Check for Robots.txt
                if current_url == onion_url.rstrip('/'): # Only check robots.txt for the base URL
                    robots_url = urljoin(current_url, '/robots.txt')
                    console.print(f"[dim]    Checking robots.txt at {robots_url}...[/dim]")
                    robots_response = _fetch_url_tor(session, robots_url, scan_timeout, console)
                    if robots_response and robots_response.status_code == 200:
                        disallowed_paths = re.findall(r"Disallow:\s*(.*)", robots_response.text, re.IGNORECASE)
                        if disallowed_paths:
                            findings.append({
                                "type": "Robots.txt Disallowed",
                                "url": robots_url,
                                "status_code": 200,
                                "title": "N/A",
                                "server_header": "N/A",
                                "description": f"Robots.txt lists disallowed paths: {', '.join([p.strip() for p in disallowed_paths if p.strip()])}. Review these areas."
                            })
                        else:
                            console.print("[dim]    No disallowed paths found in robots.txt.[/dim]")
                    elif robots_response:
                        console.print(f"[dim]    Robots.txt not found or inaccessible (Status: {robots_response.status_code}).[/dim]")
                    else:
                        console.print("[dim]    Could not fetch robots.txt.[/dim]")

                # Check Common Paths (only from base URL for efficiency, or from all crawled URLs if depth allows)
                if current_url == onion_url.rstrip('/'): # Only check common paths from the base URL to avoid excessive requests
                    for path in common_paths:
                        full_path_url = urljoin(current_url, path)
                        console.print(f"[dim]    Checking common path: {full_path_url}...[/dim]")
                        path_response = _fetch_url_tor(session, full_path_url, scan_timeout, console)
                        if path_response and path_response.status_code == 200:
                            description = f"Common path '{path}' found."
                            if "Index of /" in path_response.text:
                                description = f"Directory listing enabled at '{path}'."
                            findings.append({
                                "type": "Exposed Path",
                                "url": full_path_url,
                                "status_code": path_response.status_code,
                                "title": get_page_title(path_response.text) if path_response.text else "N/A",
                                "server_header": path_response.headers.get('Server', 'N/A'),
                                "description": description
                            })
                        elif path_response:
                            console.print(f"[dim]    Path {path} not found (Status: {path_response.status_code}).[/dim]")
                        else:
                            console.print(f"[dim]    Could not fetch path {path}.[/dim]")


                # Extract and queue new internal .onion links for further crawling
                if current_depth < depth:
                    links = extract_onion_links(response.text, current_url)
                    for link in links:
                        if link not in visited_urls:
                            queue.append((link, current_depth + 1))
                            console.print(f"[dim]    Queued new link: {link} (Next Depth: {current_depth + 1})[/dim]")
                            logger.debug(f"Queued link: {link} (Depth: {current_depth + 1})")
            else:
                logger.warning(f"Skipping further analysis for {current_url} due to fetch error.")
    
    logger.info(f"Scan of {onion_url} completed. Found {len(findings)} findings.")
    return findings

