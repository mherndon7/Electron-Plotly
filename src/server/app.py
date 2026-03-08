import asyncio
from calendar import c
from pathlib import Path

import tornado

index_file = (
    Path(__file__).parent.parent.parent
    / "dist"
    / "electron-app"
    / "browser"
    / "index.html"
)


class CookieHandler(tornado.web.RequestHandler):

    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", " http://localhost:4200")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def get(self):
        cookie_name = self.application.settings.get("cookie_name", None)
        cookie_value = self.application.settings.get("cookie_value", None)

        if cookie_name and cookie_value:
            cookie = self.get_cookie(cookie_name)
            if cookie and cookie == cookie_value:
                self.write(f"Cookie '{cookie_name}' found with value: {cookie}")
            elif cookie:
                self.write(
                    f"Cookie '{cookie_name}' found but value mismatch. "
                    f"Expected: {cookie_value}, Got: {cookie}"
                )
            else:
                self.write(f"Cookie '{cookie_name}' not found.")
        else:
            self.write("No cookie name or value configured in application settings.")


class StaticFileHandler(tornado.web.StaticFileHandler):

    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    # def prepare(self):
    # self.set_secure_cookie("session_token", "manually_set_token")
    # print("Cookie:", self.get_secure_cookie("session_token"))


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
