import os
from typing import Dict, Any, Optional, List, Iterator

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from data_sources.abstract import DataSource


# Pydantic models for Higyrus API
class DatosPrincipalesFisicas(BaseModel):
    """Data model for main personal information."""
    nombres: str
    apellidos: str
    tipoId: str
    id: str


class DatosPersonales(BaseModel):
    """Data model for personal details."""
    paisOrigen: Optional[str] = None
    nacionalidad: Optional[str] = None
    paisResidencia: Optional[str] = None
    lugarNacimiento: Optional[str] = None


class DatosFiscalesNacionales(BaseModel):
    """Data model for fiscal information."""
    CUIT: str
    actividadesEconomicasAFIP: List[Any] = []


class MedioComunicacion(BaseModel):
    """Data model for communication methods."""
    tipoMedio: str
    medio: str
    vigenteDesde: Optional[str] = None
    vigenteHasta: Optional[str] = None
    uso: str
    principal: bool
    notas: Optional[str] = None


class Domicilio(BaseModel):
    """Data model for addresses."""
    uso: Optional[str] = None
    vigenteDesde: Optional[str] = None
    vigenteHasta: Optional[str] = None
    pais: Optional[str] = None
    provincia: Optional[str] = None
    ciudad: Optional[str] = None
    codigoPostal: Optional[str] = None
    calle: Optional[str] = None
    altura: Optional[str] = None
    piso: Optional[str] = None
    departamento: Optional[str] = None
    notas: Optional[str] = None


class Declaracion(BaseModel):
    """Data model for declarations."""
    personaPEP: Optional[bool] = None
    sujetoObligado: Optional[bool] = None
    personaEstadounidense: Optional[bool] = None
    numeroInscripcion: Optional[str] = None
    observaciones: Optional[str] = None
    validadoPor: Optional[List[Any]] = None
    fechaUltimaValidacion: Optional[str] = None


class Person(BaseModel):
    """
    Data model for a person from Higyrus API.
    """
    datosPrincipalesFisicas: Optional[DatosPrincipalesFisicas]
    datosPersonales: Optional[DatosPersonales] = None
    datosFiscalesNacionales: Optional[DatosFiscalesNacionales] = None
    mediosComuniacion: Optional[List[MedioComunicacion]] = None
    domiciliosSimples: Optional[List[Domicilio]] = None
    declaraciones: Optional[List[Declaracion]] = None
    datosPrincipalesIdeal: Optional[Any] = None
    datosOrganizacion: Optional[Any] = None
    gruposEconomicos: Optional[List[Any]] = None
    informacionPatrimonial: Optional[List[Any]] = None
    patrimonioYBalance: Optional[Any] = None
    notas: Optional[List[Any]] = None
    autoridades: Optional[Any] = None
    accionistas: Optional[Any] = None
    usuarios: Optional[List[Any]] = None
    domicilioUrbano: Optional[Any] = None


class HigyrusAPIClient:
    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None):
        load_dotenv()

        # Set API credentials and URL
        self.base_url = base_url or os.getenv("HIGYRUS_API_URL")
        self.username = username or os.getenv("HIGYRUS_API_USER")
        self.password = password or os.getenv("HIGYRUS_API_PASSWORD")

        if not self.base_url:
            raise ValueError("Higyrus API URL is not set. Please set HIGYRUS_API_URL environment variable.")
        if not self.username:
            raise ValueError("Higyrus API username is not set. Please set HIGYRUS_API_USER environment variable.")
        if not self.password:
            raise ValueError("Higyrus API password is not set. Please set HIGYRUS_API_PASSWORD environment variable.")

        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]

        self.token = None

    def login(self) -> bool:
        login_url = f"{self.base_url}/login"
        payload = {
            "clientId": "",
            "username": self.username,
            "password": self.password
        }

        try:
            response = requests.post(login_url, json=payload)
            response.raise_for_status()

            data = response.json()
            if "token" not in data:
                raise ValueError("Token not found in login response")

            self.token = data["token"]
            return True
        except requests.RequestException as e:
            print(f"Login failed: {e}")
            return False

    def _ensure_authenticated(self) -> None:
        if not self.token:
            if not self.login():
                raise ValueError("Authentication required but login failed")

    def _json_to_person(self, json_data: Dict[str, Any]) -> Person:
        # Keep a copy of the data for error reporting
        processed_data = json_data.copy()

        # No need to pre-process None values for list fields anymore
        # as they are now defined as Optional in the Person class

        try:
            return Person.model_validate(json_data)
        except ValidationError as e:
            # best effort to show the validation error
            error_msg = f"Validation error for Person object:\n{e}\n"

            error_msg += "\nProblematic data:\n"

            for error in e.errors():
                field_path = error.get('loc', [])
                field_name = '.'.join(str(p) for p in field_path)

                value = processed_data
                try:
                    for part in field_path:
                        if isinstance(part, int) and isinstance(value, list) and part < len(value):
                            value = value[part]
                        elif isinstance(part, str) and isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = "N/A"
                            break
                except (KeyError, IndexError, TypeError):
                    value = "N/A"

                error_msg += f"  Field '{field_name}': {error.get('msg', 'Unknown error')}\n"
                error_msg += f"  Value: {value}\n"
                error_msg += f"  Type: {type(value).__name__}\n\n"

            raise ValueError(error_msg)

    def list_persons(self) -> List[Person]:
        self._ensure_authenticated()

        url = f"{self.base_url}/personas/listadoPersonas"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            json_data = response.json()

            persons = []
            validation_errors = []
            discarded_count = 0

            for i, person_data in enumerate(json_data):
                try:
                    person = self._json_to_person(person_data)

                    # Check for companies and report them as excluded
                    if person.datosPrincipalesFisicas is None:
                        discarded_count += 1
                        if person.datosPrincipalesIdeal and 'denominacion' in person.datosPrincipalesIdeal:
                            print(
                                f"Discarded potential company known as: {person.datosPrincipalesIdeal['denominacion']}")
                        else:
                            print(f"Discarded person at index {i} (Unknown name)")
                    else:
                        persons.append(person)
                except ValueError as e:
                    error_msg = f"Error processing person at index {i}:\n{str(e)}"
                    validation_errors.append(error_msg)

            if discarded_count > 0:
                print(f"INFO: Discarded {discarded_count} persons with null datosPrincipalesFisicas")

            if validation_errors:
                error_summary = "\n\n".join(validation_errors)
                print(
                    f"WARNING: Encountered {len(validation_errors)} validation errors while processing persons:\n{error_summary}")

                if not persons:
                    raise ValueError(f"All {len(json_data)} person records failed validation:\n{error_summary}")

            return persons

        except requests.RequestException as e:
            print(f"Failed to list persons: {e}")
            if response.status_code == 401:
                self.token = None
                # poor man retry logic ;-)
                return self.list_persons()
            raise


class HigyrusDataSource(DataSource):
    """
    Data source implementation that retrieves data from the Higyrus API.
    """

    def __init__(self, client: Optional[HigyrusAPIClient] = None):
        self._client = client or HigyrusAPIClient()
        self._persons = None

    @property
    def name(self) -> str:
        return "Higyrus"

    def _ensure_data_loaded(self) -> None:
        if self._persons is None:
            if not self._client.token:
                self._client.login()
            self._persons = self._client.list_persons()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        self._ensure_data_loaded()

        for person in self._persons:
            yield self._person_to_dict(person)

    def _person_to_dict(self, person: Person) -> Dict[str, Any]:
        data = {}

        if person.datosPrincipalesFisicas:
            data["nombre"] = getattr(person.datosPrincipalesFisicas, "nombres", None)
            data["apellido"] = getattr(person.datosPrincipalesFisicas, "apellidos", None)
            data["tipoDocumento"] = getattr(person.datosPrincipalesFisicas, "tipoId", None)
            data["numeroDocumento"] = getattr(person.datosPrincipalesFisicas, "id", None)

        if person.datosPersonales:
            for field_name in person.datosPersonales.model_fields.keys():
                data[field_name] = getattr(person.datosPersonales, field_name, None)

        if person.datosFiscalesNacionales:
            data["CUIT"] = getattr(person.datosFiscalesNacionales, "CUIT", None)

        # maps "tipoMedio" value as a column, and "medio" as a value plus some normalization to minimize column names explosion
        # adds ordinal to column name if value reoccurs
        if person.mediosComuniacion:
            medio_counts = {}
            for medio in person.mediosComuniacion:
                tipo = getattr(medio, "tipoMedio", "")
                if tipo:
                    tipo_mapping = {
                        "E-Mail": "email",
                        "Telefono": "telefono",
                        "Teléfono": "telefono"
                    }
                    tipo = tipo_mapping.get(tipo, tipo)

                    if tipo in medio_counts:
                        medio_counts[tipo] += 1
                        column_name = f"{tipo}{medio_counts[tipo]}"
                    else:
                        medio_counts[tipo] = 1
                        column_name = tipo

                    data[column_name] = getattr(medio, "medio", None)

        # Only include address when "Real" (ignoring Legal)
        if person.domiciliosSimples:
            for domicilio in person.domiciliosSimples:
                if getattr(domicilio, "uso", "") == "Real":
                    data["pais"] = getattr(domicilio, "pais", None)
                    data["provincia"] = getattr(domicilio, "provincia", None)
                    data["calle"] = getattr(domicilio, "calle", None)
                    data["altura"] = getattr(domicilio, "altura", None)
                    data["codigoPostal"] = getattr(domicilio, "codigoPostal", None)
                    break

        data["source"] = self.name

        return data

    def get_columns(self) -> List[str]:
        columns = [
            # From datosPrincipalesFisicas
            "nombre", "apellido", "tipoDocumento", "numeroDocumento",

            # From datosPersonales
            "paisOrigen", "nacionalidad", "paisResidencia", "lugarNacimiento",

            # From datosFiscalesNacionales
            "CUIT",

            # From domiciliosSimples (when uso is "Real")
            "pais", "provincia", "calle", "altura", "codigoPostal",

            # Source identifier
            "source"
        ]

        # From mediosComuniacion
        common_medio_types = ["email", "telefono"]
        for tipo in common_medio_types:
            columns.append(tipo)

        return columns
