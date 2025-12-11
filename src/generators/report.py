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
    
    """
    docx = DocxTemplate(template)

    date = datetime.now()

    context = {
        'repository_name': Path(repository).resolve().name,
        'analysis_date': date.strftime('%A, %B %d, %Y'),
        'summary': {
            'repository_goal': '',
            'scope': '',
            'key_points': [
                '',
                '',
                '',
                # ...
            ],
        },
        'global_stats': _global_stats(framework, modules),
        'modules_overview': _modules_overview(repository, modules),
        'hotspots': [
            {
                'module': '',
                'sloc': 0,
                'percent_of_total': '0%',
                'comment': '',
            },
            # ...
        ],
        'complexity_notes': [
            '',
            '',
            # ...
        ],
        'doc_coverage': _doc_coverage(modules),
        'best_documented_modules': [
            {
                'name': '', 
                'percent': 0
            },
            # ...
        ],
        'worst_documented_modules': [
            {
                'name': '', 
                'percent': 0
            },
            # ...
        ],
        'dependencies': {
            'independent_modules': 0,
            'avg_dependencies': 0,
            'core_modules': [
                '', 
                '',
                # ...
            ],
            'summary': '',
        },
        'risks': [
            '',
            '',
            # ...
        ],
        'risk_impact': {
            'maintainability': '',
            'onboarding': '',
            'evolution': '',
            # ...
        },
        'recommendations': {
            'refactor': [
                '',
                # ...
            ],
            'docs': [
                '',
                # ...
            ],
            'architecture': [
                '',
                # ...
            ],
        },
        'version': ALGORITHM_VERSION
    }

    docx.render(context)

    path = os.path.join(output, FILE)

    docx.save(path)

    return path

def _global_stats(framework: str, modules: List['ModuleInfo']) -> Dict[str, Union[str, int]]:
    """
    
    """
    loc = 0
    sloc = 0

    for module in modules:
        if module.metrics:
            loc += module.metrics.loc or 0
            sloc += module.metrics.sloc or 0

    return {
        'languages': framework.capitalize(),
        'n_files': len(modules),
        'total_loc': loc,
        'total_sloc': sloc
    }

def _modules_overview(repository: str, modules: List['ModuleInfo']) -> List[Dict[str, Union[str, int]]]:
    """
    
    """
    out = []

    for module in sorted(modules, key=lambda module: module.path):
        if module.metrics:
            out.append({
                'path': Path(module.path).resolve().relative_to(Path(repository).resolve()).name,
                'loc': module.metrics.loc,
                'sloc': module.metrics.sloc,
                'n_classes': module.metrics.n_classes,
                'n_methods': module.metrics.n_methods,
                'n_functions': module.metrics.n_functions
            })

    return out

def _doc_coverage(modules: List['ModuleInfo']) -> Dict[str, int]:
    """
    
    """
    class_percent = 0
    method_percent = 0 
    attribute_percent = 0

    return {
        'class_percent': class_percent,
        'method_percent': method_percent,
        'attribute_percent': attribute_percent,
    }










# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE