"""
Lexer and directory autodiscovery module for env-sync.
Scans repository subdirectories deterministically and validates directive syntax and tokens.
"""

import os
import re
from typing import List, Dict, Set, Tuple


class LexicalError(Exception):
    """Raised when a directive token is invalid, unrecognized, or references an intermediate directory."""
    pass


class SyntaxError(Exception):
    """Raised when a directive or variable line has invalid syntax."""
    pass


EXCLUDED_DIR_NAMES = {".terraform", ".git", ".idea", ".vscode", "__pycache__"}


def _is_dir_excluded(dir_name: str) -> bool:
    """Checks if a directory should be skipped by the scanner."""
    if dir_name.startswith("."):
        return True
    if dir_name in EXCLUDED_DIR_NAMES:
        return True
    return False


def _has_tf_files(dir_path: str) -> bool:
    """Checks if a directory directly contains at least one .tf file."""
    if not os.path.isdir(dir_path):
        return False
    try:
        for entry in os.listdir(dir_path):
            if entry.endswith(".tf") and os.path.isfile(os.path.join(dir_path, entry)):
                return True
    except OSError:
        pass
    return False


def discover_leaf_modules(parent_abs_path: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Recursively scans parent_abs_path to find all Terraform leaf modules.
    
    A directory is a leaf module if:
    1. It directly contains at least one .tf file.
    2. None of its subdirectories (recursively) contains .tf files.
    
    Returns:
    - valid_leaf_tokens: List of relative paths from parent_abs_path (e.g. ['bootstrap', 'github/oidc'])
    - intermediate_map: Map of intermediate directories to their leaf children (e.g. {'github': ['github/oidc', ...]})
    """
    if not os.path.isdir(parent_abs_path):
        return [], {}

    all_tf_dirs: Set[str] = set()

    for root, dirs, files in os.walk(parent_abs_path):
        # Filter out excluded directories in-place
        dirs[:] = [d for d in dirs if not _is_dir_excluded(d)]
        
        has_tf = any(f.endswith(".tf") for f in files)
        if has_tf:
            rel_dir = os.path.relpath(root, parent_abs_path)
            all_tf_dirs.add(rel_dir)

    # Determine leaf modules (dirs in all_tf_dirs that have no descendant in all_tf_dirs)
    leaf_modules: List[str] = []
    for tf_dir in sorted(all_tf_dirs):
        # Check if any other tf_dir starts with tf_dir + "/"
        is_leaf = True
        for other in all_tf_dirs:
            if other != tf_dir and other.startswith(tf_dir + os.sep):
                is_leaf = False
                break
        if is_leaf:
            # Normalize path separators to forward slash
            leaf_modules.append(tf_dir.replace(os.sep, "/"))

    # Build intermediate map for helpful error diagnostics
    intermediate_map: Dict[str, List[str]] = {}
    for root, dirs, _ in os.walk(parent_abs_path):
        dirs[:] = [d for d in dirs if not _is_dir_excluded(d)]
        rel_root = os.path.relpath(root, parent_abs_path).replace(os.sep, "/")
        if rel_root == ".":
            continue
        
        # Find which leaf modules belong under this directory
        children = [leaf for leaf in leaf_modules if leaf.startswith(rel_root + "/")]
        if children and rel_root not in leaf_modules:
            intermediate_map[rel_root] = children

    return leaf_modules, intermediate_map


# Regex for validating directive syntax: [token1 | token2 | ...]
DIRECTIVE_PATTERN = re.compile(r"^\s*\[(.*)\]\s*$")


def parse_and_validate_directive(
    line: str,
    valid_leaf_tokens: List[str],
    intermediate_map: Dict[str, List[str]],
    line_num: int,
    file_name: str,
) -> List[str]:
    """
    Parses a directive line (e.g. `[bootstrap | github/oidc]`) and validates its tokens.
    Returns the list of target tokens, or `['*']` for wildcard.
    Raises SyntaxError or LexicalError if invalid.
    """
    match = DIRECTIVE_PATTERN.match(line)
    if not match:
        raise SyntaxError(
            f"Error Sintáctico en {file_name}, línea {line_num}: "
            f"Línea de directiva malformada: '{line.strip()}'. Formato esperado: [modulo1 | modulo2]"
        )

    inner = match.group(1).strip()
    if not inner:
        raise SyntaxError(
            f"Error Sintáctico en {file_name}, línea {line_num}: "
            f"Directiva vacía '[]' no está permitida."
        )

    # Split by pipe
    parts = [p.strip() for p in inner.split("|")]

    # Check for empty parts like [| a] or [a |] or [a || b]
    if any(len(p) == 0 for p in parts):
        raise SyntaxError(
            f"Error Sintáctico en {file_name}, línea {line_num}: "
            f"Directiva contiene pipes sin operandos: '{line.strip()}'"
        )

    # Check for wildcard
    if "*" in parts:
        if len(parts) > 1:
            raise SyntaxError(
                f"Error Sintáctico en {file_name}, línea {line_num}: "
                f"El wildcard '[*]' no se puede combinar con módulos específicos: '{line.strip()}'"
            )
        return ["*"]

    # Validate each token
    target_tokens: List[str] = []
    for token in parts:
        # Check token syntax: alphanumeric with dash, underscore, forward slash
        if not re.match(r"^[a-zA-Z0-9_\-\/]+$", token):
            raise SyntaxError(
                f"Error Sintáctico en {file_name}, línea {line_num}: "
                f"Nombre de módulo inválido '{token}' en directiva."
            )

        if token in valid_leaf_tokens:
            target_tokens.append(token)
        elif token in intermediate_map:
            valid_children = ", ".join(intermediate_map[token])
            raise LexicalError(
                f"Error Léxico en {file_name}, línea {line_num}:\n"
                f"  Token '{token}' no es un módulo hoja válido.\n"
                f"  '{token}' contiene subdirectorios con módulos Terraform.\n"
                f"  Tokens válidos para esta ruta: {valid_children}"
            )
        else:
            valid_list = ", ".join(valid_leaf_tokens) if valid_leaf_tokens else "(ninguno)"
            raise LexicalError(
                f"Error Léxico en {file_name}, línea {line_num}:\n"
                f"  Token '{token}' no existe en el scope del directorio asociado.\n"
                f"  Tokens válidos disponibles: {valid_list}"
            )

    return target_tokens
