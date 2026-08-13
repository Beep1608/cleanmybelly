"""
env_sync package: Unified environment and Terraform variables synchronization tool.
"""

from .scope_map import SCOPE_MAP, get_repo_root, validate_env_files_exist
from .lexer import discover_leaf_modules, parse_and_validate_directive, LexicalError, SyntaxError
from .parser import parse_env_file, parse_variables_tf, parse_tfvars_file, parse_backend_file, has_s3_backend
from .synchronizer import synchronize_all

__all__ = [
    "SCOPE_MAP",
    "get_repo_root",
    "validate_env_files_exist",
    "discover_leaf_modules",
    "parse_and_validate_directive",
    "LexicalError",
    "SyntaxError",
    "parse_env_file",
    "parse_variables_tf",
    "parse_tfvars_file",
    "parse_backend_file",
    "has_s3_backend",
    "synchronize_all",
]
