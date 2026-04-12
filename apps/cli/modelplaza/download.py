import click
import httpx
from rich.console import Console

from modelplaza.config import get_api_url, get_token

console = Console()


@click.command()
@click.argument("model_path", metavar="OWNER/SLUG")
@click.option("--output", "-o", help="Output directory", default=".")
def download_cmd(model_path: str, output: str):
    """Download a model from Model Plaza.

    MODEL_PATH should be in the format owner/slug (e.g. alice/my-model).
    """
    if "/" not in model_path:
        console.print("[red]Model path must be in format: owner/slug[/red]")
        return

    owner, slug = model_path.split("/", 1)
    token = get_token()
    api_url = get_api_url()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = httpx.get(
            f"{api_url}/models/{owner}/{slug}/download",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        download_url = data.get("download_url")
        if not download_url:
            console.print("[yellow]No files available for download[/yellow]")
            return

        console.print(f"[green]Download URL: {download_url}[/green]")
        console.print("[dim]Use curl or wget to download the file[/dim]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Download failed: {e.response.json().get('detail', 'Unknown error')}[/red]")
    except httpx.ConnectError:
        console.print("[red]Cannot connect to API. Is the server running?[/red]")
