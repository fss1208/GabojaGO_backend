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