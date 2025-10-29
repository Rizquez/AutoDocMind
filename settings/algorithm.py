# LIBRERIAS (EXTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
# ---------------------------------------------------------------------------------------------------------------------

# LIBRERIAS (INTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
from settings.constants import FOLDER_OUTPUT
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIVO / CREACION DE CLASE(S) / FUNCIONES GENERALES
# ---------------------------------------------------------------------------------------------------------------------

class Settings:
    """
    Clase que construye y gestiona la configuracion especifica para la ejecucion del algoritmo.

    **Proposito:**
        - Centralizar la carga de argumentos de entrada.
        - Definir y preparar las rutas necesarias para almacenar la salida de los archivos generados.

    Al instanciar esta clase, se generan automaticamente las rutas de salida y los recursos necesarios.
    """

    def __init__(self, args: 'Namespace') -> None:
        self.__lang = args.lang
        self.__repo = args.repo

        if args.output:
            self.__output = os.path.join(args.output, FOLDER_OUTPUT)
        else:
            self.__output = os.path.join(self.__get_root(), FOLDER_OUTPUT)

    @property
    def lang(self) -> str:
        return self.__lang
    
    @property
    def repo(self) -> str:
        return self.__repo
    
    @property
    def output(self) -> str:
        return self.__output
    
    @staticmethod
    def __get_root() -> str:
        """
        Este metodo estatico determina la ruta absoluta del archivo actual, 
        elimina el ultimo nivel del directorio y devuelve la ruta resultante.

        Returns:
            str: 
                Ruta absoluta del directorio raiz del proyecto.
        """
        return '\\'.join(item for item in os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])

# ---------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO