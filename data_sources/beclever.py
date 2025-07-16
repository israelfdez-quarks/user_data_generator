import os
from typing import Dict, Any, Optional, List, Iterator

from dotenv import load_dotenv

from data_sources.abstract import DataSource


class BeCleverClient:
    """
    Client for connecting to the BeClever SQL Server database.
    """

    def __init__(self, db_conn_str: Optional[str] = None):
        load_dotenv()

        self.db_conn_str = db_conn_str or os.getenv("BECLEVER_DB_CONN_STR")

        # Do not crash all if missing local dependencies
        try:
            import pyodbc
            self._pyodbc = pyodbc
        except ImportError:
            self._pyodbc = None

        print(f"BeCleverClient initialized with connection string")

    def query_users(self) -> List[Dict[str, Any]]:
        conn = self._pyodbc.connect(self.db_conn_str)
        cursor = conn.cursor()

        query = """
                select C.Nom                                as nombre,
                       C.Ape + ' ' + C.Ape2                 as apellido,
                       C.NumDoc                             as numeroDocumento,
                       IIF(C.IdTipoCliente = 1, 'PF', 'PJ') as tipoPersona,
                       C.PreFijCel + C.TelCel               as Movil,
                       C.Mai                                as email,
                       C.TelCel2                            as Movil2,
                       C.Mai2                               as email2,
                       C.FecAlt                             as created_at,
                       C.NumDocFis                          as CUIT,
                       C.Pep                                as pep,
                       NAC.Des                              as nacionalidad,
                       CADDR.Num                            as altura,
                       CADDR.CodPos                         as codigoPostal,
                       CADDR.Cal                            as calle,
                       COUNTRY.Des                          as paisResidencia,
                       PROV.Des                             as provincia,
                       CT.IdCuenta                          as numeroCuentaAL2,
                       ACC.CVU                              as AL2CVU,
                       ACC.Ali                              as AL2Alias,
                       CI.Nom + ' ' + CI.Nom2               as nombreApoderadoAL2,
                       CI.Ape + ' ' + CI.Ape2               as apellidoApoderadoAL2,
                       CI.NumDoc                            as numeroDocumentoApoderadoAL2,
                       CI.NumDocFis                         as CUITApoderadoAL2,
                       CI.Mai                               as emailApoderadoAL2,
                       CI.TelCel                            as MovilApoderadoAL2
                from CLIENTES C
                         left join Nacionalidades NAC on C.IdNacionalidad = NAC.IdNacionalidad
                         left join CLIENTESDOMICILIO CADDR
                                   on C.IdCliente = CADDR.IdCliente and CADDR.IdTipoDomicilio = 1
                         left join PAISES COUNTRY on CADDR.IdPais = COUNTRY.IdPais
                         left join PROVINCIAS PROV on CADDR.IdProvincia = PROV.IdProvincia
                         join CUENTAS CT on C.IdCliente = CT.IdCliente
                         left join CUENTA_PRODUCTOS ACC on CT.IdCuenta = ACC.IdCuenta
                         left join CUENTAINTERVINIENTES CI on CT.IdCuenta = CI.IdCuenta
                ORDER BY C.NumDocFis
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
            "numeroDocumento",
            "tipoPersona",
            "Movil",
            "email",
            "Movil2",
            "email2",
            "created_at",
            "CUIT",
            "pep",
            "nacionalidad",
            "altura",
            "codigoPostal",
            "calle",
            "paisResidencia",
            "provincia",
            "numeroCuentaAL2",
            "AL2CVU",
            "AL2Alias",
            "nombreApoderadoAL2",
            "apellidoApoderadoAL2",
            "numeroDocumentoApoderadoAL2",
            "CUITApoderadoAL2",
            "emailApoderadoAL2",
            "MovilApoderadoAL2",
            "source"
        ]

        return columns
