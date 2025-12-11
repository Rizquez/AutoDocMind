# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from dataclasses import dataclass
from typing import List, Dict, Union
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['ModuleMetrics', 'RepositoryMetrics']

@dataclass
class ModuleMetrics:
    """
    It contains basic metrics extracted from a source module.

    Attributes:
        loc (int):
            Total number of lines in the file, including comments, blank lines, and code.
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        n_classes (int):
            Total number of classes detected in the module.
        n_functions (int):
            Number of functions defined at the module level.
        n_methods (int):
            Total number of methods defined within all classes of the module.
    """
    loc: int
    sloc: int
    n_classes: int
    n_functions: int
    n_methods: int

@dataclass
class RepositoryMetrics:
    """
    # TODO: Documentar
    
    Attributes:
        loc (int):
        sloc (int):
        class_percent (Union[float, int]):
        method_percent (Union[float, int]):
        attribute_percent (Union[float, int]):
        module_stats (List[Dict[str, Union[str, int]]]):
        modules_overview (List[Dict[str, Union[str, int]]]):
    """
    loc: int
    sloc: int
    class_percent: Union[float, int]
    method_percent: Union[float, int]
    attribute_percent: Union[float, int]
    module_stats: List[Dict[str, Union[str, int]]]
    modules_overview: List[Dict[str, Union[str, int]]]
    
# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE