from datetime import datetime

class LOG:

    @staticmethod
    def TO_ESTIMATED_TIME(dt: datetime) -> str:
        return f"{(dt - datetime.now()).total_seconds() / 1000:.2f} ms"
