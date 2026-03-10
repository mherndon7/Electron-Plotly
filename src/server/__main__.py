import mimetypes

from server.cli import cli

# Ensure the correct mime type is registered
mimetypes.init()
mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("text/javascript", ".js", True)

if __name__ == "__main__":
    cli()
