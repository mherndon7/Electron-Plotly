import asyncio

import click

from .app import start_server
from .authentication import create_private_pem, generate_keypair, get_signed_cookie


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
def generate_cookie(cookie_name: str, developer_mode: bool):
    _, private_key, user_secret = generate_keypair()
    if developer_mode:
        user_secret = "development_cookie_secret"

    private_pem = create_private_pem(private_key, user_secret)
    cookie_value = get_signed_cookie(private_pem, user_secret)
    click.echo(f"{cookie_name}::{cookie_value}")


@cli.command()
@click.option(
    "--cookie-name",
    "-cn",
    default="aether_token",
    help="The name of the cookie to set.",
)
@click.option(
    "--cookie-secret",
    "-cs",
    help="The session token cookie secret.",
    default="development_cookie_secret",
)
@click.option(
    "--cookie-secret",
    "-cs",
    help="The session token cookie secret.",
    default="development_cookie_secret",
)
@click.option(
    "developer_mode",
    "--dev",
    is_flag=True,
    default=False,
    help="Generate a cookie for development purposes.",
)
def server(cookie_name: str, cookie_secret: str, developer_mode: bool):
    ctx = click.get_current_context()
    parameter_source = ctx.get_parameter_source("cookie_secret")

    if not developer_mode and parameter_source == click.core.ParameterSource.DEFAULT:
        raise click.BadParameter(
            "Cookie value must be provided when not in development mode.",
            param_hint="cookie_value",
        )

    _, private_key, _ = generate_keypair()
    private_pem = create_private_pem(private_key, cookie_secret)
    cookie_value = get_signed_cookie(private_pem, cookie_secret)

    click.echo(
        f"Starting server with cookie name: {cookie_name},"
        f" cookie secret {cookie_secret},"
        f" and cookie value: {cookie_value}"
    )
    asyncio.run(
        start_server(
            cookie_name,
            cookie_value,
            cookie_secret,
            private_pem,
        )
    )
