import hashlib
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.progress import Progress

from modelplaza.config import get_api_url, get_token

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--slug", required=True, help="Model slug (e.g. my-model)")
@click.option("--version", "version_tag", default="v1", help="Version tag")
@click.option("--framework", help="Framework (pytorch, tensorflow, etc.)")
@click.option("--task", help="Task type (text-generation, etc.)")
@click.option("--license", "license_type", help="License (apache-2.0, mit, etc.)")
@click.option("--description", help="Model description")
def upload_cmd(
    path: str,
    slug: str,
    version_tag: str,
    framework: str | None,
    task: str | None,
    license_type: str | None,
    description: str | None,
):
    """Upload a model file to Model Plaza."""
    token = get_token()
    if not token:
        console.print("[red]Not logged in. Run: mp login[/red]")
        return

    api_url = get_api_url()
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create model repo (if it doesn't exist)
    create_data = {"slug": slug}
    if framework:
        create_data["framework"] = framework
    if task:
        create_data["task"] = task
    if license_type:
        create_data["license_type"] = license_type
    if description:
        create_data["description"] = description

    try:
        resp = httpx.post(
            f"{api_url}/models",
            json=create_data,
            headers={**headers, "Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code == 201:
            console.print(f"[green]Created model repo: {slug}[/green]")
        elif resp.status_code == 409:
            console.print(f"[dim]Model repo {slug} already exists[/dim]")
        else:
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Failed to create model: {e.response.text}[/red]")
        return

    # Step 2: Get owner username
    me_resp = httpx.get(f"{api_url}/auth/me", headers=headers, timeout=10)
    me_resp.raise_for_status()
    owner = me_resp.json()["username"]

    # Step 3: Upload file
    file_path = Path(path)
    file_size = file_path.stat().st_size

    # Compute hash locally
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    content_hash = sha256.hexdigest()
    console.print(f"[dim]SHA-256: {content_hash}[/dim]")

    with Progress() as progress:
        task_id = progress.add_task("Uploading...", total=file_size)
        with open(file_path, "rb") as f:
            resp = httpx.post(
                f"{api_url}/models/{owner}/{slug}/upload",
                params={"version_tag": version_tag},
                files={"file": (file_path.name, f)},
                headers=headers,
                timeout=600,
            )
            progress.update(task_id, completed=file_size)

    if resp.status_code == 200:
        version = resp.json()
        console.print(f"[green]Uploaded {file_path.name} as {version_tag}[/green]")
        console.print(f"[dim]Content hash: {version.get('content_hash', 'N/A')}[/dim]")
        console.print(
            f"[dim]On-chain registration will happen in the background[/dim]"
        )
    else:
        console.print(f"[red]Upload failed: {resp.text}[/red]")
