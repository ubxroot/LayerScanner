#!/usr/bin/env python3
# LayerScanner: Advanced Multi-Blockchain Transaction Tracer (Onion Web Scanner)
# Designed to be run directly on Kali Linux.
# Ensure all required packages are installed globally:
# sudo pip install typer rich "requests[socks]" pyfiglet beautifulsoup4

import typer
import json
import sys
import re # For robots.txt parsing in scanner (already in scanner, but good to note)
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.markup import escape
import pyfiglet # For the banner

# Import core and utils modules
from core.scanner import scan_onion_site
from utils.logger import setup_logger
from utils.config import load_config

# Initialize Typer app and Rich console
app = typer.Typer(help="🕵️ LayerScanner - Advanced Onion Web Scanning Tool")
console = Console()

# --- ASCII Banner ---
LAYERSCANNER_BANNER = Text()
LAYERSCANNER_BANNER.append(pyfiglet.figlet_format("LayerScanner", font="slant"), style="bold magenta")
LAYERSCANNER_BANNER.append("\n")
LAYERSCANNER_BANNER.append("Comprehensive Information Gathering for Onion Websites\n", style="bright_cyan")
LAYERSCANNER_BANNER.append("github.com/ubxroot/LayerScanner (Placeholder)\n", style="dim white")

@app.command(name="scan", help="Scan an .onion website for information and common vulnerabilities.")
def scan_command(
    onion_url: str = typer.Argument(..., help="The .onion URL to scan (e.g., http://example.onion/)."),
    depth: int = typer.Option(1, "--depth", "-d", help="Maximum crawl depth for internal links. 0 for base URL only."),
    output_format: str = typer.Option("human", "--output", "-o", help="Output format: human (default) or json."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose logging output.")
):
    """
    Initiates a scan of the specified .onion website, gathering information
    and checking for common configurations and exposed paths.
    """
    console.print(LAYERSCANNER_BANNER) # Display banner at the start
    
    logger = setup_logger()
    if verbose:
        logger.setLevel(logging.DEBUG) # Set logger to DEBUG if verbose is enabled
        console.print("[dim]Verbose logging enabled.[/dim]")

    config = load_config()

    # Basic URL validation for .onion
    if not onion_url.startswith("http://") and not onion_url.startswith("https://"):
        onion_url = "http://" + onion_url # Default to http for onion
    
    if not onion_url.endswith(".onion") and not onion_url.endswith(".onion/"):
        console.print("[bold red]Error:[/bold red] The provided URL does not appear to be an .onion address. Please ensure it ends with '.onion'.")
        sys.exit(1)

    console.print(f"\n[bold blue]LayerScanner:[/bold blue] Scanning [green]{onion_url}[/green] (Depth: {depth})\n")
    logger.info(f"Starting scan for {onion_url} with depth={depth}")

    try:
        # Call the core scanning function
        findings = scan_onion_site(onion_url, depth, logger, config, console)

        if output_format == "json":
            console.print(json.dumps(findings, indent=2))
        else:
            console.print("\n[bold yellow]--- Scan Results ---[/bold yellow]")
            if findings:
                table = Table(title=f"Findings for {onion_url}", show_header=True, header_style="bold magenta", expand=True)
                table.add_column("Type", style="bold green", min_width=15)
                table.add_column("URL", style="cyan", min_width=30)
                table.add_column("Status", style="blue", justify="center", min_width=8)
                table.add_column("Title/Header", style="white", min_width=20)
                table.add_column("Description", style="yellow", min_width=40)

                for finding in findings:
                    status_code = finding.get("status_code", "N/A")
                    status_style = "green" if str(status_code).startswith('2') else ("yellow" if str(status_code).startswith('3') else "red")
                    
                    table.add_row(
                        Text(finding.get("type", "N/A"), style="bold white"),
                        Text(finding.get("url", "N/A"), style="cyan"),
                        Text(str(status_code), style=status_style),
                        Text(finding.get("title", finding.get("server_header", "N/A")), style="white"), # Display title or server header
                        Text(finding.get("description", "N/A"), style="yellow")
                    )
                console.print(table)
            else:
                console.print("[bold green]No significant findings or information gathered for this onion site.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ An unexpected error occurred during scan: {escape(str(e))}[/bold red]")
        logger.error(f"Error during scan: {e}", exc_info=True)
        sys.exit(1)

    console.print(f"\n[bold green]LayerScanner scan complete.[/bold green]")

if __name__ == "__main__":
    app()

