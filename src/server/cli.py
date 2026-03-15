import asyncio

import click

from .app import start_server
from .authentication import create_private_pem, generate_keypair, get_signed_cookie
from .log import log_splash_status


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--cookie-name",
    "-cn",
    default="aether_token",
    help="The name of the cookie to set.",
)
@click.option(
    "developer_mode",
    "--dev",
    is_flag=True,
    default=False,
    help="Generate a cookie for development purposes.",
)
def server(cookie_name: str, developer_mode: bool):

    _, private_key, cookie_secret = generate_keypair()
    if developer_mode:
        cookie_secret = "development_cookie_secret"

    private_pem = create_private_pem(private_key, cookie_secret)
    cookie_value = get_signed_cookie(private_pem, cookie_secret)
    click.echo(f"Cookie::{cookie_name}::{cookie_value}")

    click.echo(
        f"Starting server with cookie name: {cookie_name},"
        f" cookie secret {cookie_secret},"
        f" and cookie value: {cookie_value}"
    )
    log_splash_status(10, "Starting server...")

    asyncio.run(
        start_server(
            cookie_name,
            cookie_value,
            cookie_secret,
            private_pem,
            developer_mode,
        )
    )
