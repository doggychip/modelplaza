import httpx

from config import settings


async def _get_headers() -> dict:
    if settings.gitea_admin_token:
        return {"Authorization": f"token {settings.gitea_admin_token}"}
    # Fall back to basic auth
    return {}


async def _get_auth() -> tuple[str, str] | None:
    if not settings.gitea_admin_token:
        return (settings.gitea_admin_user, settings.gitea_admin_password)
    return None


async def create_gitea_repo(username: str, repo_name: str) -> dict | None:
    """Create a repository in Gitea for storing model files via Git LFS."""
    url = f"{settings.gitea_url}/api/v1/user/repos"
    headers = await _get_headers()
    auth = await _get_auth()

    # First ensure the user exists in Gitea, create if not
    await ensure_gitea_user(username)

    # Create repo under the admin account, then transfer if needed
    # For MVP, all repos live under the admin org
    payload = {
        "name": f"{username}--{repo_name}",
        "description": f"Model repository for {username}/{repo_name}",
        "private": False,
        "auto_init": True,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, auth=auth, timeout=30)
            if resp.status_code in (201, 200):
                return resp.json()
            if resp.status_code == 409:
                # Repo already exists
                return {"id": None, "name": payload["name"]}
            resp.raise_for_status()
    except httpx.HTTPError:
        # Don't block model creation if Gitea is down
        return None


async def ensure_gitea_user(username: str):
    """Check if user exists in Gitea, create if not."""
    url = f"{settings.gitea_url}/api/v1/users/{username}"
    headers = await _get_headers()
    auth = await _get_auth()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, auth=auth, timeout=10)
            if resp.status_code == 200:
                return  # User exists

            # Create user
            create_url = f"{settings.gitea_url}/api/v1/admin/users"
            payload = {
                "username": username,
                "email": f"{username}@modelplaza.local",
                "password": "placeholder-will-use-token-auth",
                "must_change_password": False,
            }
            await client.post(create_url, json=payload, headers=headers, auth=auth, timeout=10)
    except httpx.HTTPError:
        pass  # Non-fatal


async def delete_gitea_repo(username: str, repo_name: str):
    """Delete a Gitea repository."""
    url = f"{settings.gitea_url}/api/v1/repos/{settings.gitea_admin_user}/{username}--{repo_name}"
    headers = await _get_headers()
    auth = await _get_auth()

    try:
        async with httpx.AsyncClient() as client:
            await client.delete(url, headers=headers, auth=auth, timeout=10)
    except httpx.HTTPError:
        pass
