import asyncio

import click

from .app import start_server


@click.group()
def cli():
    pass


@cli.command()
def generate_cookie():
    click.echo("session_token::super_secret_server_value")


@cli.command()
def server():
    asyncio.run(start_server())
