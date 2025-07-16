from typing import List

from data_sources import DataSource


class MockDataSource(DataSource):

    def __init__(self):
        self._persons = None

    @property
    def name(self) -> str:
        return "Mock"

    def _ensure_data_loaded(self) -> None:
        if self._persons is None:
            # Create some mock data
            self._persons = [
                {"numeroDocumento": "mock-001", "nombre": "John", "apellido": "Doe", "email": "john.doe@example.com",
                 "telefono": "+1234567890", "direccion": "123 Main St", "ciudad": "New York", "provincia": "NY",
                 "pais": "USA", "source": self.name},
                {"numeroDocumento": "mock-002", "nombre": "Jane", "apellido": "Smith",
                 "email": "jane.smith@example.com",
                 "telefono": "+0987654321", "direccion": "456 Oak Ave", "ciudad": "Los Angeles", "provincia": "CA",
                 "pais": "USA", "source": self.name}]

    def __iter__(self):
        self._ensure_data_loaded()
        for person in self._persons:
            yield person

    def get_columns(self) -> List[str]:
        return ["numeroDocumento", "nombre", "apellido", "email", "telefono", "direccion", "ciudad", "provincia",
                "pais", "source"]
