import os
import random
from typing import Dict, Any, Optional, List, Iterator

from dotenv import load_dotenv

from data_sources.abstract import DataSource


class BeCleverClient:
    """
    Client for connecting to the BeClever database.
    """

    def __init__(self, db_url: Optional[str] = None, db_user: Optional[str] = None,
                 db_password: Optional[str] = None):
        load_dotenv()

        self.db_url = db_url or os.getenv("BECLEVER_DB_URL") or "mock://beclever-db"
        self.db_user = db_user or os.getenv("BECLEVER_DB_USER") or "mock_user"
        self.db_password = db_password or os.getenv("BECLEVER_BB_PASSWORD") or "mock_password"

        print(f"BeCleverClient initialized with URL: {self.db_url}")
        print(f"Using mock data for BeClever database")

    def query_users(self) -> List[Dict[str, Any]]:
        # For now, generate mock data
        mock_users = []

        # Generate 10 mock users
        for i in range(10):
            user = {
                "nombre": f"Nombre{i + 1}",
                "apellido": f"Apellido{i + 1}",
                "CUIT": f"20-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}",
                "email": f"usuario{i + 1}@example.com",
                "telefono": f"+54 9 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            }
            mock_users.append(user)

        return mock_users


class BeCleverDataSource(DataSource):

    def __init__(self, client: Optional[BeCleverClient] = None):
        self._client = client or BeCleverClient()
        self._users = None

    @property
    def name(self) -> str:
        return "BeClever"

    def _ensure_data_loaded(self) -> None:
        if self._users is None:
            self._users = self._client.query_users()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        self._ensure_data_loaded()

        for user in self._users:
            # Add source identifier
            user_data = user.copy()
            user_data["source"] = self.name
            yield user_data

    def get_columns(self) -> List[str]:
        columns = [
            "nombre",
            "apellido",
            "CUIT",
            "email",
            "telefono",
            "source"
        ]

        return columns
