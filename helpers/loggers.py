# LIBRERIAS (EXTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
import os
import logging
from typing import TYPE_CHECKING
from logging.handlers import RotatingFileHandler

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# LIBRERIAS (INTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
from settings.constants import ALGORITHM, FILE_LOG

if TYPE_CHECKING:
    from settings.algorithm import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIVO / CREACION DE CLASE(S) / FUNCIONES GENERALES
# ---------------------------------------------------------------------------------------------------------------------

class ManageLogger:
    """
    Clase encargada de gestionar la configuracion del logger utilizado en la aplicacion.

    Esta clase centraliza la inicializacion y configuracion de logger para la capa de `Algoritmo`. 

    Su objetivo es asegurar que cada componente de la aplicacion tenga un sistema de logging consistente y separado.

    **Puntos clave:**
        - **Niveles distintos:** 
            - Algoritmo → admite `DEBUG`, `INFO`, `WARNING`, `ERROR`.
    """

    @classmethod
    def algorithm(cls, settings: 'Settings') -> None:
        """
        Configura el logger asociado a la capa de **Algoritmo**.

        Args:
            settings (Settings):
                Objeto que contiene los ajustes generales para la ejecucion del algoritmo.
        """
        folder = settings.output
        
        os.makedirs(folder, exist_ok=True)

        file = os.path.join(folder, f'{FILE_LOG}.log')

        logger = logging.getLogger(ALGORITHM)
        if logger.handlers: 
            return # Evita duplicar handlers si ya se configuro antes
        
        # El fichero solo guarda INFO/ERROR/WARNING, aunque el logger acepte DEBUG
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(cls.__handler(file))
        logger.addHandler(cls.__stream_handler())
        
    @staticmethod
    def close_logger(logger: 'Logger') -> None:
        """
        Cierra y elimina todos los handlers asociados a un logger especifico.

        - Recorre todos los handlers activos del logger.
        - Cierra cada handler para liberar descriptores de archivo.
        - Remueve los handlers del logger para dejarlo limpio.

        Args:
            logger (Logger):
                Instancia del logger que se desea cerrar.
        """
        lst_handlers = logger.handlers[:]
        for handler in lst_handlers:
            handler.close()
            logger.removeHandler(handler)

    @staticmethod
    def __handler(
        file: str, 
        *, 
        level: int = logging.INFO, 
        size: int = 1024 * 1024 * 5,
        backup: int = 10,
        encoding: str = 'utf-8'
    ) -> RotatingFileHandler:
        """
        Crea un `RotatingFileHandler` para escribir los logs en un fichero con rotacion automatica.

        Args:
            file (str):
                Ruta completa del archivo de log.
            level (int, optional):
                Nivel de log.
            size (int, optional):
                Maximo tamaño que podra tener el fichero antes de realizar la copia de seguridad.
            backup (int, optional):
                Cantidad de copias de seguridad que se podran generar.
            encoding (str, optional):
                Formato de codificacion para la escritura del fichero log.

        Returns:
            RotatingFileHandler:
                Handler configurado con formato y rotacion.
        """
        handler = RotatingFileHandler(
            file, 
            maxBytes=size, 
            backupCount=backup, 
            encoding=encoding,
            delay=True # El fichero se crea recien cuando se escribe el primer log
        )

        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(level)

        return handler
    
    @staticmethod
    def __stream_handler() -> logging.StreamHandler:
        """
        Crea un `StreamHandler` para mostrar los logs directamente en consola.

        Returns:
            logging.StreamHandler:
                Handler configurado para salida estandar.
        """
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        handler.setLevel(logging.DEBUG) # Consola mostrara DEBUG (mas detallado que el fichero)

        return handler

# ---------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO