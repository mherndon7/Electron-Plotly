from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Awaitable, cast

import tornado
from tornado.httputil import HTTPServerRequest

from .authentication import authenticate

if TYPE_CHECKING:
    from .app import ServerApplication

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    def __init__(
        self,
        application: "ServerApplication",
        request: HTTPServerRequest,
        **kwargs: Any,
    ) -> None:
        super().__init__(application, request, **kwargs)
        self.application = cast("ServerApplication", self.application)

    def get_current_user(self):
        return authenticate(self)

    def prepare(self) -> Awaitable[None] | None:
        authenticate(self)
        logger.debug("Authenticated!")
        return super().prepare()


class CookieHandler(BaseHandler):
    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", " http://localhost:4200")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def get(self):
        logger.debug(f"Current user: {self.current_user}")

        cookie_name = self.application.cookie_name
        cookie_value = self.application.cookie_value

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


class StaticFileHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
