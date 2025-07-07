# core/parser.py

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Optional

def get_page_title(html_content: str) -> Optional[str]:
    """Extracts the <title> from HTML content."""
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    return title_tag.get_text(strip=True) if title_tag else None

def extract_onion_links(html_content: str, base_url: str) -> List[str]:
    """
    Extracts unique .onion links from HTML content that belong to the same hidden service.
    Filters out external .onion links or non-.onion links.
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    found_links = set()
    base_netloc = urlparse(base_url).netloc # e.g., "example.onion"

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)

        # Check if it's an .onion domain and belongs to the same hidden service
        if parsed_url.netloc.endswith('.onion') and parsed_url.netloc == base_netloc:
            # Ensure it's a valid URL and not just a fragment or empty link
            if parsed_url.scheme and parsed_url.netloc:
                # Reconstruct URL without query parameters or fragments for uniqueness in crawling
                clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                found_links.add(clean_url.rstrip('/')) # Remove trailing slash for consistency
    
    return list(found_links)

