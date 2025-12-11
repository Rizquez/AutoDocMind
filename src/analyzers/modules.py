# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from typing import TYPE_CHECKING, List
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models import ReportInfo
from src.tools.nums import percentage

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['analyze_modules']

def analyze_modules(modules: List['ModuleInfo'], repository: str, framework: str) -> ReportInfo:
    """

    """
    loc = 0
    sloc = 0

    total_classes = 0
    documented_classes = 0

    total_methods = 0
    documented_methods = 0

    total_attributes = 0
    documented_attributes = 0

    summary = {}
    modules_overview = []
    hotspots = []
    complexity_notes = []
    best_documented_modules = []
    worst_documented_modules = []
    dependencies = {}
    risks = []
    risk_impact = {}
    recommendations = {}

    for module in sorted(modules, key=lambda module: module.path):
        metrics = module.metrics

        if not metrics:
            continue

        modules_overview.append({
            'path': Path(module.path).resolve().relative_to(Path(repository).resolve()).name,
            'loc': metrics.loc,
            'sloc': metrics.sloc,
            'n_classes': metrics.n_classes,
            'n_methods': metrics.n_methods,
            'n_functions': metrics.n_functions
        })
        
        loc += metrics.loc or 0
        sloc += metrics.sloc or 0

        for cls in module.classes:
            total_classes += 1
            if cls.doc and cls.doc.strip():
                documented_classes += 1

            for meth in cls.methods:
                total_methods += 1
                if meth.doc and meth.doc.strip():
                    documented_methods += 1

            for attr in cls.attributes:
                total_attributes += 1
                if attr.doc and attr.doc.strip():
                    documented_attributes += 1

    global_stats = {
        'languages': framework.capitalize(),
        'n_files': len(modules),
        'total_loc': loc,
        'total_sloc': sloc
    }

    doc_coverage = {
        'class_percent': percentage(documented_classes, total_classes),
        'method_percent': percentage(documented_methods, total_methods),
        'attribute_percent': percentage(documented_attributes, total_attributes),
    }

    return ReportInfo(
        summary=summary,
        global_stats=global_stats,
        modules_overview=modules_overview,
        hotspots=hotspots,
        complexity_notes=complexity_notes,
        doc_coverage=doc_coverage,
        best_documented_modules=best_documented_modules,
        worst_documented_modules=worst_documented_modules,
        dependencies=dependencies,
        risks=risks,
        risk_impact=risk_impact,
        recommendations=recommendations
    )

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE