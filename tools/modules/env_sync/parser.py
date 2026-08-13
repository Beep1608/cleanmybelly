"""
Parser module for env-sync.
Parses .env DSL files, variables.tf declarations, terraform.tfvars, and backend.tfbackend configs.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from .lexer import parse_and_validate_directive, SyntaxError, LexicalError


# Regex for parsing variable lines: [!]var_name = "value"
VARIABLE_LINE_PATTERN = re.compile(r"^(!?)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$")


def parse_env_file(
    env_file_path: str,
    valid_leaf_tokens: List[str],
    intermediate_map: Dict[str, List[str]],
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Parses a .env file containing directives and variable assignments.
    
    Returns a dictionary mapping each leaf module token to its effective variables:
    {
        "module_token": {
            "input_vars": {"var_name": "val", ...},
            "backend_vars": {"terraform_state_bucket": "val", ...}
        }
    }
    """
    file_name = os.path.basename(env_file_path)
    if not os.path.isfile(env_file_path):
        raise FileNotFoundError(f"Archivo de entorno no encontrado: {env_file_path}")

    # Initialize container for each discovered leaf module
    modules_data: Dict[str, Dict[str, Dict[str, str]]] = {
        token: {"input_vars": {}, "backend_vars": {}} for token in valid_leaf_tokens
    }

    current_targets: Optional[List[str]] = None

    with open(env_file_path, "r", encoding="utf-8") as f:
        for line_idx, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Skip blank lines and full comment lines
            if not line or line.startswith("#"):
                continue

            # Check if this line is a directive header [...]
            if line.startswith("[") and line.endswith("]"):
                current_targets = parse_and_validate_directive(
                    line, valid_leaf_tokens, intermediate_map, line_idx, file_name
                )
                continue

            # Variable assignment line
            if current_targets is None:
                raise SyntaxError(
                    f"Error Sintáctico en {file_name}, línea {line_idx}: "
                    f"Variable declarada fuera de una directiva: '{line}'. "
                    f"Debe declarar una directiva como [*] o [modulo] antes de las variables."
                )

            var_match = VARIABLE_LINE_PATTERN.match(line)
            if not var_match:
                raise SyntaxError(
                    f"Error Sintáctico en {file_name}, línea {line_idx}: "
                    f"Línea de variable malformada: '{line}'. "
                    f"Formato esperado: nombre_variable = \"valor\" o !backend_var = \"valor\""
                )

            is_backend_prefix, var_name, raw_value = var_match.groups()
            is_backend = bool(is_backend_prefix)

            # Clean quoted value
            value = raw_value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            # Resolve which leaf modules receive this variable
            target_modules = valid_leaf_tokens if current_targets == ["*"] else current_targets

            for mod_token in target_modules:
                if mod_token not in modules_data:
                    continue

                category = "backend_vars" if is_backend else "input_vars"
                # Set or override variable value according to precedence
                modules_data[mod_token][category][var_name] = value

    return modules_data


# Regex to parse Terraform variable declarations in variables.tf
TF_VARIABLE_DECLARATION = re.compile(
    r'variable\s+"([a-zA-Z_][a-zA-Z0-9_]*)"\s*\{(?:[^{}]*|\{[^{}]*\})*\}',
    re.MULTILINE | re.DOTALL,
)


def parse_variables_tf(variables_tf_path: str) -> List[str]:
    """
    Parses a variables.tf file and returns the list of declared variable names.
    """
    if not os.path.isfile(variables_tf_path):
        return []

    with open(variables_tf_path, "r", encoding="utf-8") as f:
        content = f.read()

    return TF_VARIABLE_DECLARATION.findall(content)


def parse_tfvars_file(tfvars_path: str) -> Dict[str, str]:
    """
    Parses a terraform.tfvars or .tfvars.example file into a dictionary of {var_name: value}.
    """
    if not os.path.isfile(tfvars_path):
        return {}

    result = {}
    with open(tfvars_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                k = key.strip()
                v = val.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                result[k] = v

    return result


def parse_backend_file(backend_path: str) -> Dict[str, str]:
    """
    Parses a backend.tfbackend or .tfbackend.example file into a dictionary of {key: value}.
    """
    return parse_tfvars_file(backend_path)


def has_s3_backend(module_dir_path: str) -> bool:
    """
    Checks whether a leaf module has an S3 backend block defined in its .tf files.
    """
    if not os.path.isdir(module_dir_path):
        return False

    for entry in os.listdir(module_dir_path):
        if entry.endswith(".tf"):
            file_path = os.path.join(module_dir_path, entry)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if 'backend "s3"' in content or "backend 's3'" in content:
                        return True
            except OSError:
                pass

    return False
