from app.models.user import User
from app.core.config import settings
from app.repositories.user_repository import UserRepository


class UserService:
    """Coordinate user authentication and registration use cases."""

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def authenticate_user(self, username: str, password: str) -> User | None:
        if not username or not password:
            return None
        return self.user_repository.find_by_credentials(username, password)

    def authenticate_admin(self, username: str, password: str) -> User | None:
        if (
            not settings.admin_password
            or username != settings.admin_username
            or password != settings.admin_password
        ):
            return None
        return User(username=username)

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str | None = None,
        phone_number: str | None = None,
    ) -> User | None:
        if not email or not password or not first_name:
            return None
        return self.user_repository.create_user(
            email, password, first_name, last_name, phone_number
        )


user_service = UserService()