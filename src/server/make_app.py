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
        # self.write("This is the cookie handler. Check the console for cookie details.")
        print(self.get_secure_cookie("session_token"))
        if not self.get_cookie("session_token"):
            self.set_cookie("session_token", "manually_set_token")
            self.write("Your session token was not set yet!")
        else:
            self.write(
                f"Your session token was set! Value: {self.get_cookie('session_token')}"
            )


class StaticFileHandler(tornado.web.StaticFileHandler):

    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    # def prepare(self):
    # self.set_secure_cookie("session_token", "manually_set_token")
    # print("Cookie:", self.get_secure_cookie("session_token"))


def make_app():
    return tornado.web.Application(
        [
            (r"/cookie", CookieHandler),
            (
                r"/(.*)",
                StaticFileHandler,
                {
                    "path": index_file.parent,
                    "default_filename": index_file.name,
                },
            ),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    )
