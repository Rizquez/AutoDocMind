# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import TYPE_CHECKING, List, Dict, Union
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.tools.nums import percentage
from common.constants import ALGORITHM_VERSION
from src.utils.metrics import repository_metrics

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['generate_report']

FILE = 'Report.docx'

summary = {}
dependencies = {}
risks = []
risk_impact = {}
recommendations = {}

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

    ## TODO
    - Clean row empty on tables.
    - Delete spaces amoung the bullets.
    """
    docx = DocxTemplate(template)

    statistics = repository_metrics(modules, repository)

    date = datetime.now()

    context = {
        'repository_name': f"{Path(repository).resolve().name}.",
        'analysis_date': f"{date.strftime('%A, %B %d, %Y')}.",
        'summary': summary,
        'global_stats': _global_stats(
            statistics.loc, 
            statistics.sloc, 
            framework, 
            modules
        ),
        'modules_overview': statistics.modules_overview,
        'hotspots': _hotspots(
            statistics.sloc, 
            statistics.module_stats
        ),
        'complexity_notes': _complexity_notes(
            statistics.sloc, 
            statistics.module_stats
        ),
        'doc_coverage': _doc_coverage(
            statistics.class_percent, 
            statistics.method_percent, 
            statistics.attribute_percent
        ),
        'best_documented_modules': _best_documented_modules(
            statistics.module_stats
        ),
        'worst_documented_modules': _worst_documented_modules(
            statistics.module_stats
        ),
        'dependencies': dependencies,
        'risks': risks,
        'risk_impact': risk_impact,
        'recommendations': recommendations,
        'version': ALGORITHM_VERSION
    }

    docx.render(context)

    path = os.path.join(output, FILE)

    docx.save(path)

    return path

def _global_stats(loc: int, sloc: int, framework: str, modules: List['ModuleInfo']) -> Dict[str, Union[str, int]]:
    """
    ## TODO
    - Documentar
    """
    return {
        'languages': f"{framework.capitalize()}.",
        'n_files': f"{len(modules)}.",
        'total_loc': f"{loc}.",
        'total_sloc': f"{sloc}."
    }

def _hotspots(sloc: int, module_stats: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
    """
    ## TODO
    - Documentar
    """
    if not sloc:
        return []
    
    candidates = []

    for stats in module_stats:
        if not stats['sloc']:
            continue

        sloc_percent = percentage(stats['sloc'], sloc)

        doc_percent = percentage(stats['documented_items'], stats['total_items']) if stats['total_items'] else 0

        reasons = []

        if sloc_percent >= 20:
            reasons.append("Very large module (\u2265 20\u0025 of total SLOC).")
        elif sloc_percent >= 10:
            reasons.append("Relevant module by size (\u2265 10\u0025 of total SLOC).")
        else:
            pass

        if stats['n_methods'] >= 15:
            reasons.append("Many methods (potentially high complexity).")

        if stats['total_items'] and doc_percent <= 50:
            reasons.append("Low documentation coverage (\u2264 50\u0025).")

        if not reasons:
            continue

        candidates.append({
            'name': stats['name'],
            'sloc': stats['sloc'],
            'percent': f'{sloc_percent}\u0025',
            'comment': '\n'.join(reasons)
        })

    return sorted(
        candidates, 
        key=lambda candidate: (candidate['percent'], candidate['sloc']),
        reverse=True
    )

def _doc_coverage(
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int]
) -> Dict[str, str]:
    """
    ## TODO
    - Documentar
    """
    return {
        'class_percent': f"{class_percent}\u0025.",
        'method_percent': f"{method_percent}\u0025.",
        'attribute_percent': f"{attribute_percent}\u0025."
    }

def _complexity_notes(sloc: int, module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 10) -> List[str]:
    """
    ## TODO
    - Documentar
    """
    notes = []

    if not sloc or not module_stats:
        return notes
    
    n_modules = len(module_stats)

    # Average size and methods per module
    avg_sloc = int(sloc / n_modules)

    total_methods = sum(int(module['n_methods']) for module in module_stats)

    avg_methods = total_methods / n_modules if n_modules else 0
    avg_methods = int(avg_methods) if avg_methods.is_integer() else avg_methods

    notes.append(
        f"The project contains {n_modules} modules with an average size of "
        f"{avg_sloc} SLOC and about {avg_methods:.1f} methods per module."
    )

    # Identify very large modules by absolute size
    LARGE_SLOC = 1000  # heuristic threshold
    large_modules = [module for module in module_stats if int(module['sloc']) >= LARGE_SLOC]

    if large_modules:
        names = ', '.join(module['name'] for module in large_modules[:limit])

        if len(large_modules) == 1:
            notes.append(
                f"One module exceeds {LARGE_SLOC} SLOC ({names}), "
                "which may indicate high structural complexity."
            )
        else:
            notes.append(
                f"{len(large_modules)} modules exceed {LARGE_SLOC} SLOC "
                f"({names}), concentrating a significant amount of logic."
            )

    # Concentration in the code base: the top 20% of modules by SLOC.
    sorted_by_sloc = sorted(
        module_stats,
        key=lambda module: int(module['sloc']),
        reverse=True
    )

    top_count = max(1, int(n_modules * 0.2))
    top_modules = sorted_by_sloc[:top_count]
    sloc_top = sum(int(module['sloc']) for module in top_modules)
    sloc_top_percent = percentage(sloc_top, sloc)

    if sloc_top_percent >= 50:
        names = ', '.join(module['name'] for module in top_modules[:limit])
        notes.append(
            f"A small group of modules ({top_count} modules: {names}) "
            f"contains about {sloc_top_percent}\u0025 of the total SLOC."
        )

    # Modules with many methods (possible “God objects”)
    MANY_METHODS = 30  # heuristic threshold
    heavy_method_modules = [module for module in module_stats if int(module['n_methods']) >= MANY_METHODS]

    if heavy_method_modules:
        names = ', '.join(m['name'] for m in heavy_method_modules[:limit])
        notes.append(
            f"Some modules declare a large number of methods ({MANY_METHODS} or more), "
            f"which may complicate maintenance ({names})."
        )

    return notes[:limit]

def _best_documented_modules(module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 5) -> List[str]:
    """
    ## TODO
    - Documentar
    """
    candidates = []

    for stats in module_stats:
        total_items = stats['total_items']
        documented_items = stats['documented_items']

        if not total_items:
            continue

        doc_percent = percentage(documented_items, total_items)

        candidates.append({
            'name': f"{stats['name']}:",
            'text':f"{doc_percent}\u0025 of this module is documented.",
            'percent': doc_percent,
        })

    return sorted(
        candidates,
        key=lambda candidate: candidate['percent'],
        reverse=True
    )[:limit]

def _worst_documented_modules(module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 5) -> List[str]:
    """
    ## TODO
    - Documentar
    """
    candidates = []

    for stats in module_stats:
        total_items = stats['total_items']
        documented_items = stats['documented_items']

        if not total_items:
            continue

        doc_percent = percentage(documented_items, total_items)

        candidates.append({
            'name': f"{stats['name']}:",
            'text':f"{doc_percent}\u0025 of this module is documented.",
            'percent': doc_percent,
        })

    return sorted(
        candidates,
        key=lambda candidate: candidate['percent']
    )[:limit]

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE