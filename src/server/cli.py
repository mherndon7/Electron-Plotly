import asyncio

import click

from .app import start_server


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "developer_mode",
    "--dev",
    is_flag=True,
    default=False,
    help="Generate a cookie for development purposes.",
)
def generate_cookie(developer_mode: bool):
    if developer_mode:
        click.echo("session_token::development_cookie_value")
    else:
        click.echo("session_token::super_secret_server_value")


@cli.command()
@click.option(
    "--cookie-name",
    "-cn",
    default="session_token",
    help="The name of the cookie to set.",
)
@click.option(
    "--cookie-value",
    "-cv",
    help="The session token cookie value to set.",
    default="development_cookie_value",
)
@click.option(
    "developer_mode",
    "--dev",
    is_flag=True,
    default=False,
    help="Generate a cookie for development purposes.",
)
def server(cookie_name: str, cookie_value: str, developer_mode: bool):
    ctx = click.get_current_context()
    parameter_source = ctx.get_parameter_source("cookie_value")

    if not developer_mode and parameter_source == click.core.ParameterSource.DEFAULT:
        raise click.BadParameter(
            "Cookie value must be provided when not in development mode.",
            param_hint="cookie_value",
        )

    click.echo(
        f"Starting server with cookie name: {cookie_name} "
        f"and cookie value: {cookie_value}"
    )
    asyncio.run(start_server(cookie_name, cookie_value))
