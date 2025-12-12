# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import TYPE_CHECKING, List, Dict, Union, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from common.constants import ALGORITHM_VERSION
from src.utils.metrics import repository_metrics
from src.tools.nums import percentage, percentage_as_num, average

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

    ## TODO
    - Clean row empty on tables.
    - Delete spaces amoung the bullets.
    """
    docx = DocxTemplate(template)

    date = datetime.now()

    repo_name = Path(repository).resolve().name

    statistics = repository_metrics(modules, repository)

    dep_map = dependencies_map(modules, repository, framework)

    hotspots = _hotspots(statistics.sloc, statistics.module_stats)

    doc_coverage = _doc_coverage(
        statistics.class_percent, 
        statistics.method_percent, 
        statistics.attribute_percent
    )

    dependencies = _dependencies(dep_map, repository)

    context = {
        'repository_name': f"{repo_name}.",
        'analysis_date': f"{date.strftime('%A, %B %d, %Y')}.",
        'summary': _summary(
            statistics.sloc,
            framework,
            repo_name,
            statistics.class_percent,
            statistics.method_percent,
            statistics.attribute_percent,
            statistics.module_stats,
            hotspots
        ),
        'global_stats': _global_stats(
            statistics.loc, 
            statistics.sloc, 
            framework, 
            modules
        ),
        'modules_overview': statistics.modules_overview,
        'hotspots': hotspots,
        'complexity_notes': _complexity_notes(statistics.sloc, statistics.module_stats),
        'doc_coverage': doc_coverage,
        'best_documented_modules': _best_documented_modules(statistics.module_stats),
        'worst_documented_modules': _worst_documented_modules(statistics.module_stats),
        'dependencies': dependencies,
        'risks': _risks(
            statistics.sloc,
            statistics.class_percent,
            statistics.method_percent,
            statistics.attribute_percent,
            statistics.module_stats,
            hotspots,
            dependencies
        ),
        'risk_impact': _risk_impact(
            statistics.sloc,
            statistics.class_percent,
            statistics.method_percent,
            statistics.attribute_percent,
            hotspots,
            dependencies
        ),
        'recommendations': _recommendations(
            statistics.class_percent,
            statistics.method_percent,
            statistics.attribute_percent,
            statistics.module_stats,
            hotspots,
            dependencies
        ),
        'version': ALGORITHM_VERSION
    }

    docx.render(context)

    path = os.path.join(output, FILE)

    docx.save(path)

    return path

def _summary(
    sloc: int, 
    framework: str,
    repo_name: str,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]]
) -> Dict[str, Union[str, List[str]]]:
    """
    ## TODO
    - Documentar
    """
    key_points = []

    key_points.append(
        f"The repository contains {len(module_stats)} modules with a total of {sloc} source lines of code."
    )

    avg_doc = average([class_percent, method_percent, attribute_percent])
    if avg_doc >= 75:
        key_points.append("The overall documentation coverage is high across the codebase.")
    elif avg_doc >= 50:
        key_points.append("The documentation coverage is moderate and could be improved in some areas.")
    else:
        key_points.append("The documentation coverage is low, which may affect maintainability.")

    if hotspots:
        key_points.append(
            f"{len(hotspots)} modules concentrate a significant portion of the logic and may require special attention."
        )
    else:
        key_points.append("No significant concentration of complexity was detected across the modules.")

    return {
        'repository_goal': (
            f"This repository implements a {framework.capitalize()}-based codebase "
            f"designed to provide structured functionality within the {repo_name} project."
        ),
        'scope': (
            f"The analysis covers all detected source modules, focusing on structure, "
            f"documentation coverage, and complexity distribution."
        ),
        'key_points': key_points
    }

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

def _dependencies(
    dep_map: Dict[str, Set[str]], 
    repository: str, 
    *, 
    limit: int = 5, 
    factor: int = 2
) -> Dict[str, Union[int, float, List[str], str]]:
    """
    ## TODO
    - Documentar
    """
    if not dep_map:
        return {
            'independent_modules': 0,
            'avg_dependencies': 0,
            'core_modules': [],
            'summary': "No dependencies were detected, or the dependency map could not be constructed."
        }
    
    modules = list(dep_map.keys())

    # out-degree: how many modules each module imports
    out_degree: Dict[str, int] = {module: len(dep_map.get(module, set())) for module in modules}

    # in-degree: how many modules matter to each module
    in_degree: Dict[str, int] = {m: 0 for m in modules}
    for _, targets in dep_map.items():
        for dst in targets:
            if dst in in_degree:
                in_degree[dst] += 1
            else:
                # If a destination appears that is not listed as a key (a rare case), it will be added
                in_degree[dst] = 1
                out_degree.setdefault(dst, 0)
                dep_map.setdefault(dst, set())

    all_modules = sorted(set(list(out_degree.keys()) + list(in_degree.keys())))
    num_modules = len(all_modules)

    # Independent modules:
    #   no one imports them (out = 0)
    #   no one imports them (in = 0)
    independent = [
        module for module in all_modules
        if out_degree.get(module, 0) == 0 and in_degree.get(module, 0) == 0
    ]

    total_edges = sum(out_degree.get(module, 0) for module in all_modules)
    avg_dep = (total_edges / num_modules) if num_modules else 0
    avg_dep = int(avg_dep) if float(avg_dep).is_integer() else round(avg_dep, factor)

    # Core modules: more central modules for total connectivity (in + out)
    centrality = [
        (
            module, 
            in_degree.get(module, 0) + out_degree.get(module, 0), 
            in_degree.get(module, 0), 
            out_degree.get(module, 0)
        )
        for module in all_modules
    ]

    centrality.sort(key=lambda tpl: (tpl[1], tpl[2], tpl[3]), reverse=True)

    core_modules = [
        Path(module).resolve().relative_to(Path(repository).resolve()).name
        for (module, _, __, ___) in centrality[:limit] 
        if (in_degree.get(module, 0) + out_degree.get(module, 0)) > 0
    ]

    dense = sum(1 for module in all_modules if out_degree.get(module, 0) >= 5)
    summary_parts = []

    summary_parts.append(
        f"{num_modules} modules were analyzed and {total_edges} "
        "dependency relationships (internal imports) were detected."
    )
    summary_parts.append(
        f"The average number of dependencies per module is {avg_dep}."
    )

    if independent:
        summary_parts.append(
            f"{len(independent)} independent modules (with no incoming or outgoing dependencies) were found."
        )
    else:
        summary_parts.append(
            "No completely independent modules were found."
        )

    if core_modules:
        summary_parts.append(
            "The most central modules (with the greatest connectivity) are: " + ", ".join(core_modules) + "."
        )
    else:
        summary_parts.append(
            "No clear core modules were identified (very low or non-existent dependencies)."
        )

    if dense >= max(1, int(0.2 * num_modules)):
        summary_parts.append(
            "The structure has moderate/high interconnectivity: several modules have quite a few dependencies."
        )
    else:
        summary_parts.append(
            "The structure appears relatively modular: most modules have few dependencies."
        )

    return {
        'independent_modules': len(independent),
        'avg_dependencies': avg_dep,
        'core_modules': core_modules,
        'summary': summary_parts
    }
    
def _risks(
    sloc: int,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]],
    *,
    limit: int = 8
) -> List[str]:
    """
    ## TODO
    - Documentar
    """
    risks: List[str] = []

    if not module_stats:
        return ["Risks could not be calculated because no module statistics are available."]

    n_modules = len(module_stats)

    # Risk 1: Insufficient documentation
    avg_doc = average([class_percent, method_percent, attribute_percent])

    if avg_doc < 35:
        risks.append(
            "Low documentation coverage: increases the risk of difficult maintenance and errors when modifying the code."
        )
    elif avg_doc < 55:
        risks.append(
            "Moderate documentation coverage: some parts may be difficult to understand without context."
        )
    else:
        pass
    
    # Risk 2: Code concentration (SLOC)
    if sloc:
        sorted_by_sloc = sorted(module_stats, key=lambda module: int(module.get('sloc', 0)), reverse=True)

        top_count = max(1, int(n_modules * 0.2))

        top_modules = sorted_by_sloc[:top_count]

        top_sloc = sum(int(module.get('sloc', 0)) for module in top_modules)

        top_percent = percentage(top_sloc, sloc)

        if top_percent >= 60:
            risks.append(
                f"High concentration of logic: {top_percent}\u0025 of SLOC is in {top_count} modules."
            )

    # Risk 3: very large modules
    large = [module for module in module_stats if int(module.get('sloc', 0)) >= 1500]

    if large:
        risks.append(
            f"There are very large modules (\u2265 1500 SLOC) that may require refactoring."
        )

    # Risk 4: Too many methods in one module
    heavy_methods = [module for module in module_stats if int(module.get('n_methods', 0)) >= 40]
    if heavy_methods:
        risks.append(
            "Potentially high complexity: some modules have many methods (\u2265 40), "
            "which makes testing and changes difficult."
        )

    # Risk 5: Hotspots detected
    if hotspots:
        risks.append(
            f"Hotspots (modules critical due to size/complexity/documentation) were detected."
        )

    # Risk 6: Central dependency
    if dependencies and isinstance(dependencies.get('core_modules', None), list):
        core = dependencies.get('core_modules', [])
        if core:
            risks.append(
                f"Concentrated dependencies: there are very central modules whose modification can impact many parts."
            )

    return risks[:limit]

def _risk_impact(
    sloc: int,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]]
) -> Dict[str, List[str]]:
    """
    ## TODO
    - Documentar
    """
    avg_doc = average([class_percent, method_percent, attribute_percent])

    hot_n = len(hotspots) if hotspots else 0

    avg_deps = 0.0
    core_n = 0

    if dependencies:
        avg_deps = float(dependencies.get('avg_dependencies', 0) or 0)
        core = dependencies.get('core_modules', [])
        core_n = len(core) if isinstance(core, list) else 0

    # Maintainability
    maintainability = []

    if avg_doc < 40:
        maintainability.append(
            "The lack of documentation increases maintenance costs "
            "and the risk of errors when modifying existing code."
        )
    elif avg_doc < 60:
        maintainability.append(
            "Documentation is uneven: some parts will be easy to maintain, "
            "while others will require more time to understand."
        )
    else:
        maintainability.append(
            "Documentation coverage is reasonable and helps maintain the code with less friction."
        )

    if hot_n >= 3:
        maintainability.append(
            "The existence of several hotspots suggests areas with "
            "high logical load where changes may be more delicate."
        )
    elif hot_n == 0:
        maintainability.append(
            "No clear hotspots are detected, which usually indicates a more uniform distribution of logic."
        )
    else:
        maintainability.append(
            "There are some isolated hotspots that should be monitored to prevent them from becoming bottlenecks."
        )

    if sloc >= 20000:
        maintainability.append(
            "The total size of the code (high SLOC) implies more "
            "maintenance surface area and a greater need for consistency."
        )
    elif sloc >= 5000:
        maintainability.append(
            "The code size is medium: maintenance is manageable, but complexity should be monitored."
        )
    else:
        maintainability.append(
            "The code size is small: maintenance should be relatively easy if the structure is consistent."
        )

    # Onboarding
    onboarding = []

    if avg_doc < 40:
        onboarding.append(
            "Poor documentation hinders the onboarding of new developers and increases reliance on tacit knowledge."
        )
    elif avg_doc < 60:
        onboarding.append(
            "Onboarding will be reasonable, but some areas will require support or knowledge transfer sessions."
        )
    else:
        onboarding.append(
            "Documentation facilitates onboarding and reduces the time needed to understand the system."
        )

    if dependencies:
        if core_n >= 3:
            onboarding.append(
                "The presence of several core modules suggests that "
                "onboarding should start with those key components."
            )
        elif core_n == 0:
            onboarding.append(
                "There are no clearly central modules, which may allow for incremental learning by area."
            )
        else:
            onboarding.append(
                "There is a small set of core modules that serve as an entry point for understanding the system."
            )

        if avg_deps >= 5:
            onboarding.append(
                "The level of dependencies is relatively high, which may increase the learning curve."
            )
        elif avg_deps >= 2:
            onboarding.append(
                "Dependencies are moderate; the learning curve depends on how the domains are separated."
            )
        else:
            onboarding.append(
                "Dependencies are low, which favors understanding by isolated modules."
            )

    # Evolution (future changes)
    evolution = []

    if dependencies and core_n >= 3:
        evolution.append(
            "Changes to core modules can have a cascading impact, "
            "so it is advisable to reinforce tests and review changes."
        )
    elif dependencies and core_n > 0:
        evolution.append(
            "There is a small core whose evolution must be managed carefully to avoid collateral effects."
        )
    else:
        evolution.append(
            "The dependency structure does not show a dominant core, which may facilitate localized changes."
        )

    if hot_n >= 3:
        evolution.append(
            "Hotspots can become friction points for evolution; it is advisable to plan gradual refactors."
        )
    elif hot_n > 0:
        evolution.append(
            "Monitoring specific hotspots will help prevent too much logic from being concentrated in a few modules."
        )
    else:
        evolution.append(
            "No notable hotspots are observed, suggesting potentially more stable evolution by area."
        )

    if avg_doc < 40:
        evolution.append(
            "Improving documentation will accelerate future evolutions and reduce risk when introducing changes."
        )
    elif avg_doc < 60:
        evolution.append(
            "Strengthening documentation in critical modules will reduce the cost of evolution in the medium term."
        )
    else:
        evolution.append(
            "Current documentation helps introduce changes with greater security and predictability."
        )

    return {
        'maintainability': maintainability,
        'onboarding': onboarding,
        'evolution': evolution
    }

def _recommendations(
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]],
    *,
    limit: int = 6
) -> Dict[str, List[str]]:
    """
    ## TODO
    - Documentar
    """
    rec = {
        'refactor': [],
        'docs': [],
        'architecture': [],
    }

    if not module_stats:
        rec['architecture'].append("There are not enough module statistics to generate recommendations.")
        return rec
    
    # Base signals
    avg_doc = average([class_percent, method_percent, attribute_percent])

    core = dependencies.get('core_modules', []) if isinstance(dependencies, dict) else []
    core = core if isinstance(core, list) else []
    avg_deps = float(dependencies.get('avg_dependencies', 0) or 0) if isinstance(dependencies, dict) else 0.0
    independent = int(dependencies.get('independent_modules', 0) or 0) if isinstance(dependencies, dict) else 0

    # Top modules by SLOC (for more specific suggestions)
    sorted_by_sloc = sorted(module_stats, key=lambda module: int(module.get('sloc', 0)), reverse=True)
    big = [module for module in sorted_by_sloc if int(module.get('sloc', 0)) >= 1500]
    heavy_methods = [module for module in sorted_by_sloc if int(module.get('n_methods', 0)) >= 40]

    # Refactor
    if hotspots:
        names = ', '.join(str(hot.get('name', '')) for hot in hotspots[:limit] if hot.get('name'))
        if names:
            rec['refactor'].append(
                f"Prioritize refactoring in hotspots to reduce complexity and isolate responsibilities ({names})."
            )
        else:
            rec['refactor'].append(
                "Prioritize refactoring in hotspots to reduce complexity and isolate responsibilities."
            )

    if big:
        names = ', '.join(str(module.get('name', '')) for module in big[:limit] if module.get('name'))
        rec['refactor'].append(
            f"Split very large modules (\u2265 1500 SLOC) into smaller, testable components. ({names})."
        )

    if heavy_methods:
        names = ', '.join(str(module.get('name', '')) for module in heavy_methods[:limit] if module.get('name'))
        rec['refactor'].append(
            "Reduce modules with too many methods (\u2265 40): "
            f"extract services/helpers and simplify logic ({names})."
        )

    if not rec['refactor']:
        rec['refactor'].append(
            "No clear signs of urgent refactoring were detected; maintain periodic review of complexity."
        )

    # Documentation
    if avg_doc < 35:
        rec['docs'].append(
            "Increase base documentation: add docstrings/summaries to main classes and methods."
        )
        rec['docs'].append(
            "Document critical modules (hotspots and core modules) in particular before adding new features."
        )
    elif avg_doc < 60:
        rec['docs'].append(
            "Reinforce documentation in areas with low coverage to reduce maintenance time."
        )
        rec['docs'].append(
            "Ensure consistency of format in docstrings (Args/Returns/Raises) to facilitate automatic reading."
        )
    else:
        rec['docs'].append(
            "Maintain the current level of documentation and require minimum docstrings for relevant changes."
        )

    # If there are hotspots, specific documentation is suggested there
    if hotspots:
        names = ', '.join(str(h.get('name', '')) for h in hotspots[:limit] if h.get('name'))
        if names:
            rec['docs'].append(
                f"Add usage examples and design notes in hotspots to facilitate future modifications. ({names})."
            )

    # Architecture
    if core:
        core_names = ', '.join(str(x) for x in core[:limit])
        rec['architecture'].append(
            "Clearly define responsibilities and contracts in core "
            f"modules to minimize cascading impact. ({core_names})."
        )

    if avg_deps >= 5:
        rec['architecture'].append(
            "Reduce coupling between modules: review imports, introduce layers or interfaces where it makes sense."
        )
        rec['architecture'].append(
            "Avoid circular dependencies and reinforce boundaries between domains "
            "(for example: separate IO layer, domain, and utilities)."
        )
    elif avg_deps >= 2:
        rec['architecture'].append(
            "Review dependencies between modules to maintain clear domain separation and avoid progressive coupling."
        )
    else:
        rec['architecture'].append(
            "The dependency structure appears to be modular; maintain "
            "import discipline so that it does not deteriorate over time."
        )

    if independent >= 5:
        rec['architecture'].append(
            "Review independent modules: confirm whether they are intended as utilities, tests, or orphaned code."
        )

    rec['refactor'] = rec['refactor'][:limit]
    rec['docs'] = rec['docs'][:limit]
    rec['architecture'] = rec['architecture'][:limit]

    return rec

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE