# LIBRERIAS (EXTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# LIBRERIAS (INTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
# Se referencian aqui!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIVO / CREACION DE CLASE(S) / FUNCIONES GENERALES
# ---------------------------------------------------------------------------------------------------------------------

def error_trace(indicator: str, tb: List[Tuple[str, int, str, str]], logger: 'Logger', error: Exception) -> None:
    """
    Registra en el logger un error con informacion de la traza filtrada.

    La funcion procesa la traza de error y elimina aquellas entradas que provienen de librerias externas, las cuales 
    se ubican en `Lib\\site-packages`. De esta manera se conserva un traceback mas relevante y enfocado en el codigo 
    propio de la aplicacion.

    Args:
        indicator (str): 
            Texto indicador del contexto del error.
        tb (List[Tuple[str, int, str, str]]): 
            Trazas obtenidas con `traceback.extract_tb`.
        logger (Logger): 
            Instancia de logger donde se registrara el error.
        error (Exception): 
            Objeto de excepcion capturado.
    """
    filtered = [
        (filename, line, funcname, text) 
        for filename, line, funcname, text in tb 
        if r'Lib\site-packages' not in filename
    ]

    if not filtered:
        logger.error(f"{indicator}: {error} - No relevant traceback found")
        return
    
    filename, line, funcname, text = filtered[-1]

    logger.error(f"{indicator}: {error} in {text} on {funcname}, file {filename} in line {line}")

# ---------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO