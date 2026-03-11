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
    def __init__(self, cookie_name: str, cookie_value: str):
        self.cookie_name = cookie_name
        self.cookie_value = cookie_value

        super().__init__(
            self._handlers(),
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            cookie_name=cookie_name,
            cookie_value=cookie_value,
        )

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


async def start_server(cookie_name: str, cookie_value: str):
    app = ServerApplication(cookie_name, cookie_value)
    app.listen(8888)
    await asyncio.Event().wait()
