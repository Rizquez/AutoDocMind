# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from dataclasses import dataclass
from typing import Dict, List, Union
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['ReportInfo']

@dataclass
class ReportInfo:
    """
    Represents all the structured information needed to generate an analysis report from a repository.
    
    Attributes:
        summary (Dict[str, Union[str, List[str]]]):
            General summary of the analysis.
        global_stats (Dict[str, Union[str, int]]):
            Overall project metrics.
        modules_overview (List[Dict[str, Union[str, int]]]):
            Basic information about each module.
        hotspots (List[Dict[str, Union[str, int]]]):
            List of modules with the highest code load or relevance.
        complexity_notes (List[str]):
            General notes on the complexity detected in the project.
        doc_coverage (Dict[str, int]):
            Documentation percentages
        best_documented_modules (List[Dict[str, Union[str, int]]]):
            Modules with the best level of documentation.
        worst_documented_modules (List[Dict[str, Union[str, int]]]):
            Modules with the worst level of documentation.
        dependencies (Dict[str, Union[str, int, List[str]]]):
            Summary of dependencies between modules.
        risks (List[str]):
            Risks detected related to maintainability or structure.
        risk_impact (Dict[str, str]):
            Estimated impact of risks on the evolution and use of the project.
        recommendations ( Dict[str, List[str]]):
            Recommendations grouped by category.
    """
    summary: Dict[str, Union[str, List[str]]]
    global_stats: Dict[str, Union[str, int]]
    modules_overview: List[Dict[str, Union[str, int]]]
    hotspots: List[Dict[str, Union[str, int]]]
    complexity_notes: List[str]
    doc_coverage: Dict[str, int]
    best_documented_modules: List[Dict[str, Union[str, int]]]
    worst_documented_modules: List[Dict[str, Union[str, int]]]
    dependencies: Dict[str, Union[str, int, List[str]]]
    risks: List[str]
    risk_impact: Dict[str, str]
    recommendations: Dict[str, List[str]]

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE