# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import TYPE_CHECKING, List
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.analyzers import analyze_modules
from common.constants import ALGORITHM_VERSION

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['generate_report']

FILE = 'Report.docx'

def generate_report(template: str, output: str, repository: str, framework: str, modules: List['ModuleInfo']) -> str:
    """
    Generates a repository analysis report in DOCX format from a template.

    This function takes the results of the static analysis of the modules in a repository, 
    transforms them into a high-level data structure (`ReportInfo`), and injects them into 
    a *DOCX* template using `docxtpl`. The result is a report ready to be consulted or shared.

    Args:
        template (str):
            Path to the DOCX template file that defines the structure of the report.
        output (str):
            Path of the directory where the file will be stored. If it does not exist, it is created automatically.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.

    Returns:
        str:
            Path of the generated DOCX file.

    Raises:
        OSError:
            If a problem occurs when saving the file to the output directory.
        DocxTemplateException:
            If the template is invalid or a variable expected in the template cannot be resolved in the context.

    ## TODO: Clean row empty on tables.
    """
    docx = DocxTemplate(template)

    report = analyze_modules(modules, repository, framework)

    date = datetime.now()

    context = {
        'repository_name': Path(repository).resolve().name,
        'analysis_date': date.strftime('%A, %B %d, %Y'),
        'summary': report.summary,
        'global_stats': report.global_stats,
        'modules_overview': report.modules_overview,
        'hotspots': report.hotspots,
        'complexity_notes': report.complexity_notes,
        'doc_coverage': report.doc_coverage,
        'best_documented_modules': report.best_documented_modules,
        'worst_documented_modules': report.worst_documented_modules,
        'dependencies': report.dependencies,
        'risks': report.risks,
        'risk_impact': report.risk_impact,
        'recommendations': report.recommendations,
        'version': ALGORITHM_VERSION
    }

    docx.render(context)

    path = os.path.join(output, FILE)

    docx.save(path)

    return path

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE