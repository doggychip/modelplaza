import click

from modelplaza.auth import login_cmd, register_cmd, whoami_cmd
from modelplaza.upload import upload_cmd
from modelplaza.download import download_cmd


@click.group()
@click.version_option()
def cli():
    """Model Plaza CLI - upload, download, and manage AI models with on-chain provenance."""
    pass


cli.add_command(login_cmd, "login")
cli.add_command(register_cmd, "register")
cli.add_command(whoami_cmd, "whoami")
cli.add_command(upload_cmd, "upload")
cli.add_command(download_cmd, "download")


if __name__ == "__main__":
    cli()
