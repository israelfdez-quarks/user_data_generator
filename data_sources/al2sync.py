import os
from typing import Dict, Any, Optional, List, Iterator

from dotenv import load_dotenv

from data_sources.abstract import DataSource


class AL2SyncDBClient:
    """
    Client for connecting to the AL2Sync SQL Server database.
    """

    def __init__(self, db_conn_str: Optional[str] = None):
        load_dotenv()

        self.db_conn_str = db_conn_str or os.getenv("AL2SYNC_DB_CONN_STR")

        # Do not crash all if missing local dependencies
        try:
            import pyodbc
            self._pyodbc = pyodbc
        except ImportError:
            self._pyodbc = None

    def query_users(self) -> List[Dict[str, Any]]:
        conn = self._pyodbc.connect(self.db_conn_str)
        cursor = conn.cursor()

        query = """
                select s.NOMBRE   as nombre,
                       s.APELLIDO as apellido,
                       s.CUIT,
                       s.MAIL     as email,
                       s.FECCRE   as created_at,
                       c.NOMBRE   as cooperativa
                from dbo.SOCIOS_AL2 s
                         inner join dbo.COOPERATIVAS_AL2 C on s.COOPERATIVASID = C.ID; \
                """

        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        results = []

        for row in cursor.fetchall():
            user = {columns[i]: row[i] for i in range(len(columns))}
            results.append(user)

        cursor.close()
        conn.close()

        return results


class AL2SyncDataSource(DataSource):
    """
    Data source implementation that retrieves data from the AL2Sync SQL Server database.
    """

    def __init__(self, client: Optional[AL2SyncDBClient] = None):
        self._client = client or AL2SyncDBClient()
        self._users = None

    @property
    def name(self) -> str:
        return "AL2Sync"

    def _ensure_data_loaded(self) -> None:
        if self._users is None:
            self._users = self._client.query_users()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        self._ensure_data_loaded()

        for user in self._users:
            user["source"] = self.name
            yield user

    def get_columns(self) -> List[str]:
        columns = ["nombre", "apellido", "CUIT", "email", "created_at", "cooperativa", "source"]

        return columns
