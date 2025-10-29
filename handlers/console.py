# LIBRERIAS (EXTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
import os
from typing import TYPE_CHECKING
from argparse import ArgumentParser

if TYPE_CHECKING:
    from argparse import Namespace
# ---------------------------------------------------------------------------------------------------------------------

# LIBRERIAS (INTERNAS)
# ---------------------------------------------------------------------------------------------------------------------
# Se referencian aqui!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIVO / CREACION DE CLASE(S) / FUNCIONES GENERALES
# ---------------------------------------------------------------------------------------------------------------------

class Console:
    """
    Clase encargada de gestionar y validar los argumentos recibidos por consola.

    **Proposito:**
        - Definir los argumentos requeridos y opcionales para la ejecucion.
        - Parsear los valores introducidos por el usuario.
        - Aplicar validaciones basicas sobre los argumentos recibidos.
        - Devolver los argumentos como un objeto `Namespace` listo para usar.
    """

    @classmethod
    def arguments(cls) -> 'Namespace':
        """
        Define, procesa y valida los argumentos de consola para la ejecucion del algoritmo.

        Returns:
            Namespace: 
                Objeto con los argumentos parseados y validados.
        """
        parser = ArgumentParser(
            description="Argumentos requeridos y opcionales para ejecutar el algormitmo"
        )
        
        parser.add_argument(
            '--lang',
            required=True,
            choices=['python'],
            help="Lenguajes de programacion soportados por el algoritmo"
        )

        parser.add_argument(
            '--repo',
            required=True,
            help="Directorio del respositorio que alberga el proyecto"
        )

        parser.add_argument(
            '--output',
            help="Directorio donde se guardaran los archivos generados"
        )

        args = parser.parse_args()

        cls.__validate(args, parser)

        return args

    @staticmethod
    def __validate(args: 'Namespace', parser: ArgumentParser) -> None:
        """
        Realiza validaciones sobre los argumentos recibidos desde consola.

        Args:
            args (Namespace): 
                Argumentos parseados desde la consola.
            parser (ArgumentParser): 
                Parser utilizado para lanzar mensajes de error.

        Raises:
            SystemExit: 
                Si alguna validacion falla, se invoca `parser.error`, 
                lo que detiene la ejecucion y muestra el mensaje de 
                error correspondiente.
        """
        if not os.path.exists(args.repo):
            parser.error("El parametro enviado en `--repo` debe ser un directorio valido!")

        if args.output:
            if not os.path.exists(args.output):
                parser.error("El parametro enviado en `--output` debe ser un directorio valido!")

# ---------------------------------------------------------------------------------------------------------------------
# FIN DEL FICHERO