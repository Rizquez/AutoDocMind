# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import sys, traceback, logging
from typing import TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.analyzers import *
from src.utils.scan import scanner
from helpers.trace import error_trace
from settings.constants import ALGORITHM
from src.generators import ReadmeGenerator, HtmlGenerator

if TYPE_CHECKING:
    from settings.algorithm import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['execute']

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

def execute(settings: 'Settings') -> None:
    """
    Executes the main flow of automatic documentation generation for the project.

    **This function coordinates all stages of the AutoDocMind process:**
        1. Scans the specified repository for files in the supported language.
        2. Analyzes each file found to extract its structure (classes, functions, and docstrings).
        3. Generates a `README` file with the consolidated documentation.
    """
    logger.info(f"Scanning repository: {settings.repository}")
    files = list(scanner(settings.repository, settings.included, settings.excluded))
    logger.info(f"Number of {settings.framework} files found: {len(files)}")
    
    method = globals().get(f'analyze_{settings.framework}')

    modules = []
    for file in files:
        try:
            modules.append(method(file))
        except Exception:
            _, error, line_error = sys.exc_info()
            tb = traceback.extract_tb(line_error)
            error_trace(tb, logger, error)

    logger.info("Generating README ...")
    readme_txt = ReadmeGenerator.render(modules, settings.repository)
    readme_target = ReadmeGenerator.write(readme_txt, settings.output)
    logger.info(f"Ready README: {readme_target}")

    logger.info("Generating HTML ...")
    html_txt = HtmlGenerator.render(modules, settings.repository)
    html_target = HtmlGenerator.write(html_txt, settings.output)
    logger.info(f"Ready HTML: {html_target}")

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE