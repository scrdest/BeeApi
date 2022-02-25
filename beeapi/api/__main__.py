import typing

import click
import uvicorn
from uvicorn.main import LEVEL_CHOICES

from beeapi import constants as beeconsts
from beeapi.api import app as app_module


@click.command(context_settings={"auto_envvar_prefix": "UVICORN"})
@click.option(
    "--port",
    type=int,
    default=beeconsts.DEFAULT_API_PORT,
    help="Bind socket to this port.",
    show_default=True,
)
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload.")
@click.option(
    "--workers",
    default=None,
    type=int,
    help="Number of worker processes. Defaults to the $WEB_CONCURRENCY environment"
    " variable if available, or 1. Not valid with --reload.",
)
@click.option(
    "--log-level",
    type=LEVEL_CHOICES,
    default=None,
    help="Log level. [default: info]",
    show_default=True,
)
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload.")
def main(
    port: str,
    workers: int,
    log_level: str,
    reload: bool,
):
    uvicorn.run(
        f"{app_module.__name__}:{app_module.get_app.__name__}",
        port=port,
        workers=workers,
        log_level=log_level,
        factory=True,
        reload=reload,
    )
    return


main()
