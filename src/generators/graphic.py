# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import re
from pathlib import Path
from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict, Set
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from src.utils.graphics import map_to_graph

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['render_graphic']

FILE = 'Graphic'

def render_graphic(
    modules: List['ModuleInfo'], 
    output: str, 
    repository: str, 
    framework: str, 
    *, 
    format: str = 'svg'
) -> str:
    """
    Generates the dependency graph found between the analyzed modules.

    This method builds the internal dependency map of the code, invokes the generation of the corresponding graph, 
    and physically stores it in the user-defined path. The graph is generated according to the type of framework 
    evaluated, since each framework requires a different analysis of how the modules are structured.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        output (str):
            Path of the directory where the file will be stored. If it does not exist, it is created automatically.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        format (str, optional):
            Final format of the graph file.
    
    Returns:
        str:
            Absolute path of the generated output file.
    """
    dep_map: Dict[str, Set] = _build_map(modules, repository, framework)

    graph = map_to_graph(repository, dep_map, format)

    out = Path(output) / f'{FILE}.{format}'

    graph.render(out.with_suffix(''), cleanup=True)

    return out

def _build_map(modules: List['ModuleInfo'], repository: str, framework: str) -> Dict[str, Set]:
    """
    Build the dependency map between modules based on analysis information and the logical 
    paths of the project.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        Dict:
            Dependency structure produced by the corresponding repository and framework.
    """
    paths = _paths(modules, repository, framework)

    dep_map = dependencies_map(modules, paths)

    return dep_map

def _paths(modules: List['ModuleInfo'], repository: str, framework: str) -> Dict[str, Set[str]]:
    """
    Retrieves the logical module names along with their actual physical paths.

    This method translates the full file paths in the repository to extensionless 
    relative paths, and then converts these paths into a format fully compatible 
    with the standard way of importing modules.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        Dict:
            Dictionary where each key is a logical identifier and each value is a set of file 
            paths that implement it within the repository.

    Raises:
        ValueError:
            When the framework does not have a registered compatible method.
    """
    dct = {}

    root = Path(repository).resolve()

    for module in modules:
        if framework == 'csharp':
            for imp in getattr(module, 'imports', []):
                if imp.startswith('__ns__:'):
                    ns = imp[len('__ns__:'):]
                    dct.setdefault(ns, set()).add(module.path)
        elif framework == 'python':
            relative = Path(module.path).resolve().relative_to(root)
            name = relative.with_suffix('').as_posix().replace('/', '.')
            dct[name] = module.path
        else:
            raise ValueError(f"Check the execution parameters, the {framework} framework is not currently supported")
    
    return dct

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE