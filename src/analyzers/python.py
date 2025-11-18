# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import ast, logging
from typing import List
from pathlib import Path
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from settings.constants import ALGORITHM
from src.models.structures import FunctionInfo, ClassInfo, ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['analyze_python']

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

def analyze_python(path: Path) -> ModuleInfo:
    """
    Analyzes a Python file and extracts structural information about its modules, classes, and functions.

    The analysis uses the standard `ast` (Abstract Syntax Tree) module to inspect the source code without 
    executing it. The docstrings, names, and definition lines of each relevant entity are collected, omitting 
    non-representative nodes (such as imports or single expressions).

    **Process details:**
        - Reads the file with UTF-8 encoding (ignoring errors).
        - Generates the syntax tree with `ast.parse()`.
        - Extracts:
            * Module docstring.
            * Top-level functions (`ast.FunctionDef`).
            * Classes (`ast.ClassDef`) and their internal methods.
        - Logs a warning (`logger.warning`) for each unexpected node, showing type and summary.

    Args:
        path (Path):
            Path of the Python file to be analyzed.

    Returns:
        ModuleInfo:
            Object describing the structural content of the module, including its classes, functions, and main 
            docstring.
    """
    src = path.read_text(encoding='utf-8', errors='ignore')
    tree = ast.parse(src)
    doc = ast.get_docstring(tree)

    funcs: List[FunctionInfo] = []
    classes: List[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            funcs.append(
                FunctionInfo(
                    name=node.name,
                    lineno=node.lineno,
                    doc=ast.get_docstring(node)
                )
            )
        elif isinstance(node, ast.ClassDef):
            cls = ClassInfo(
                name=node.name,
                lineno=node.lineno,
                doc=ast.get_docstring(node)
            )

            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    cls.methods.append(FunctionInfo(
                        name=sub.name,
                        lineno=sub.lineno,
                        doc=ast.get_docstring(sub)
                    ))

            classes.append(cls)
        else:
            node_type = type(node).__name__
            lineno = getattr(node, "lineno", "?")

            # Short text representing the node
            # Limit length so as not to clutter the log
            try:
                summary = ast.dump(node, annotate_fields=True, include_attributes=False)
                summary = (summary[:120] + "...") if len(summary) > 120 else summary
            except Exception:
                summary = str(node)

            logger.warning(f"Unexpected node in {path.name} (line {lineno}): type={node_type} → {summary}")

    return ModuleInfo(
        path=str(path),
        doc=doc,
        functions=funcs,
        classes=classes
    )

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE