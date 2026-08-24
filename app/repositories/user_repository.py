import logging
from collections.abc import Generator
from contextlib import contextmanager

import pyodbc

from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Read and write users in the application database."""

    @contextmanager
    def _get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        connection = pyodbc.connect(settings.connection_string)
        try:
            yield connection
        finally:
            connection.close()

    def find_by_credentials(self, username: str, password: str) -> User | None:
        query = """
            SELECT UserId, Email, FirstName, LastName
            FROM [dbo].[User]
            WHERE Email = ?
              AND Password = ?
        """

        try:
            with self._get_connection() as connection:
                row = connection.cursor().execute(query, username, password).fetchone()
        except pyodbc.Error:
            logger.exception("Database error while checking login for %s", username)
            return None

        if row is None:
            return None
        return User(user_id=row[0], username=row[1], first_name=row[2], last_name=row[3])

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str | None = None,
        phone_number: str | None = None,
    ) -> User | None:
        query = """
            INSERT INTO [dbo].[User] (Email, Password, FirstName, LastName, PhoneNumber)
            OUTPUT INSERTED.UserId, INSERTED.Email, INSERTED.FirstName, INSERTED.LastName
            VALUES (?, ?, ?, ?, ?)
        """

        try:
            with self._get_connection() as connection:
                row = (
                    connection.cursor()
                    .execute(query, email, password, first_name, last_name, phone_number)
                    .fetchone()
                )
                connection.commit()
        except pyodbc.Error:
            logger.exception("Database error while registering %s", email)
            return None

        if row is None:
            return None
        return User(user_id=row[0], username=row[1], first_name=row[2], last_name=row[3])