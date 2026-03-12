import asyncio
from pathlib import Path

import tornado

from .handlers import CookieHandler, StaticFileHandler

index_file = (
    Path(__file__).parent.parent.parent
    / "dist"
    / "electron-app"
    / "browser"
    / "index.html"
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
    app = ServerApplication(
        cookie_name,
        cookie_value,
        cookie_secret,
        private_pem,
        developer_mode,
    )
    app.listen(8888)
    await asyncio.Event().wait()
