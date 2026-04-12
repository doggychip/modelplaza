import click
import httpx
from rich.console import Console

from modelplaza.config import get_api_url, get_token, save_token

console = Console()


@click.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login_cmd(username: str, password: str):
    """Login to Model Plaza."""
    url = f"{get_api_url()}/auth/login"
    try:
        resp = httpx.post(url, json={"username": username, "password": password}, timeout=30)
        resp.raise_for_status()
        token = resp.json()["access_token"]
        save_token(token)
        console.print(f"[green]Logged in as {username}[/green]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Login failed: {e.response.json().get('detail', 'Unknown error')}[/red]")
    except httpx.ConnectError:
        console.print("[red]Cannot connect to API. Is the server running?[/red]")


@click.command()
@click.option("--username", prompt=True)
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def register_cmd(username: str, email: str, password: str):
    """Register a new account."""
    url = f"{get_api_url()}/auth/register"
    try:
        resp = httpx.post(
            url,
            json={"username": username, "email": email, "password": password},
            timeout=30,
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        save_token(token)
        console.print(f"[green]Registered and logged in as {username}[/green]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Registration failed: {e.response.json().get('detail', 'Unknown error')}[/red]")


@click.command()
def whoami_cmd():
    """Show current logged-in user."""
    token = get_token()
    if not token:
        console.print("[yellow]Not logged in. Run: mp login[/yellow]")
        return

    url = f"{get_api_url()}/auth/me"
    try:
        resp = httpx.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        resp.raise_for_status()
        user = resp.json()
        console.print(f"[bold]{user['username']}[/bold] ({user['email']})")
        console.print(f"  Tokens: {user['token_balance']}  Rep: {user['reputation_score']}")
    except httpx.HTTPStatusError:
        console.print("[red]Session expired. Run: mp login[/red]")
