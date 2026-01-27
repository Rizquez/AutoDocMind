# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.renderers.builders.document import Document
from src.utils.maps import dependencies_map
from common.constants import ALGORITHM_VERSION
from src.utils.metrics import repository_metrics
from src.renderers.builders.insights import (
    general_summary, global_stats, complexity_notes, documentation_coverage, 
    hotspots_modules, best_documented_modules, worst_documented_modules, 
    internal_dependencies, technical_risks, risk_impact, recommendations
)

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['render_report']

PDF_FILE = 'Report.pdf'

def render_report(modules: List[ModuleInfo], output: str, repository: str, framework: str) -> str:
    """
    
    """
    path = os.path.join(output, PDF_FILE)
    doc = Document(path)
    
    doc.front_page(
        Path(repository).resolve().name,
        datetime.now().strftime('%A, %B %d, %Y'),
        ALGORITHM_VERSION
    )

    doc.build()
    return path

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE