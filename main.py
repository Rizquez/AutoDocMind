# LIBRERIAS (EXTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
import time
import psutil
import logging
# ---------------------------------------------------------------------------------------------------------------------

# LIBRERIAS (INTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
from handlers.console import Console
from settings.algorithm import Settings
from helpers.loggers import ManageLogger
from settings.constants import ALGORITHM, ALGORITHM_VERSION
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIVO / CREACION DE CLASE(S) / FUNCIONES GENERALES
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    start = time.time()

    before = psutil.virtual_memory().used

    settings = Settings(Console.arguments())

    ManageLogger.algorithm(settings)

    logger = logging.getLogger(ALGORITHM)

    logger.info("Resumen de ejecucion")
    logger.info(f"Version del algoritmo: {ALGORITHM_VERSION}")

    #manage_implement(settings)

    end = time.time()

    after = psutil.virtual_memory().used

    logger.info(f"Tiempo total de ejecucion: {round(end - start, 3)} segundos")

    logger.info(f"Memoria total consumida: {round((after - before) / pow(1024, 2), 2)} megabytes")

    ManageLogger.close_logger(logger)

# ---------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO