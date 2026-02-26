from datetime import datetime
from fastapi import Request

class LOG:

    @staticmethod
    def TO_ESTIMATED_TIME(dt: datetime) -> str:
        return f"{(dt - datetime.now()).total_seconds() / 1000:.2f} ms"

    @staticmethod
    def TO_ROUTE_TEXT(request: Request) -> str:
        route = request.scope.get("route")
        return f"{request.url.path} : {route.summary}"

    @staticmethod
    def TO_REQUEST_USER(request: Request):
        return f"{request.client.host}:{request.client.port}"

    @staticmethod
    def TO_MESSAGE(request: Request, user: str, title: str, detail: str = None, dt: datetime = None):
        return f"[{user}] {LOG.TO_ROUTE_TEXT(request)} {title} {"(%s)" % detail if detail else ""} {" >> " + LOG.TO_ESTIMATED_TIME(dt) if dt else ""}"
