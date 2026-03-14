import asyncio
import logging
import sys
from pathlib import Path

import tornado

from server.log import setup_module_logger

from .handlers import CookieHandler, StaticFileHandler

logger = logging.getLogger(__name__)


def get_log_path() -> Path:
    """Path for the server log file."""
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(__file__).parent.parent.parent
    )


def get_index_path() -> Path:
    """Path to the deployed `index.html` file."""
    return (
        Path(sys.executable).parent.parent.parent
        / "dist"
        / "electron-app"
        / "browser"
        / "index.html"
        if getattr(sys, "frozen", False)
        else (
            Path(__file__).parent.parent.parent
            / "dist"
            / "electron-app"
            / "browser"
            / "index.html"
        )
    )


class ServerApplication(tornado.web.Application):
    def __init__(
        self,
        cookie_name: str,
        cookie_value: str,
        user_secret: str,
        private_pem: bytes,
        developer_mode: bool = False,
    ):
        self.cookie_name = cookie_name
        self.cookie_value = cookie_value
        self.cookie_secret = user_secret
        self.private_pem = private_pem
        self.developer_mode = developer_mode

        super().__init__(self._handlers(), cookie_secret=user_secret)

    def _handlers(self):
        index_file = get_index_path()
        logger.debug(f"Index file path: {index_file}")
        return [
            (r"/cookie", CookieHandler),
            (
                r"/(.*)",
                StaticFileHandler,
                {
                    "path": index_file.parent,
                    "default_filename": index_file.name,
                },
            ),
        ]


async def start_server(
    cookie_name: str,
    cookie_value: str,
    cookie_secret: str,
    private_pem: bytes,
    developer_mode: bool = False,
):
    setup_module_logger("server", get_log_path())
    app = ServerApplication(
        cookie_name,
        cookie_value,
        cookie_secret,
        private_pem,
        developer_mode,
    )

    logger.info("Listening on port 8888...")
    app.listen(8888)

    await asyncio.Event().wait()
