from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None