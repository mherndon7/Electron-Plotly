import asyncio

import click

from .app import start_server


@click.group()
def cli():
    pass


@cli.command()
def cookies():
    click.echo("super_secret_value")


@cli.command()
def server():
    asyncio.run(start_server())
