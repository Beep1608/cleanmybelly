"""
Synchronizer module for env-sync.
Calculates bidirectional diffs, applies precedence hierarchy, and writes/creates
all managed files across Terraform leaf modules.
"""

import os
from typing import Dict, List, Tuple, Set
from .scope_map import SCOPE_MAP, get_repo_root, validate_env_files_exist
from .lexer import discover_leaf_modules, LexicalError, SyntaxError
from .parser import (
    parse_env_file,
    parse_variables_tf,
    parse_tfvars_file,
    parse_backend_file,
    has_s3_backend,
)


def _format_tfvars_content(var_dict: Dict[str, str], is_example: bool = False) -> str:
    """Formats a dictionary of variables into HCL tfvars syntax."""
    lines = []
    for k in sorted(var_dict.keys()):
        val = "" if is_example else var_dict[k]
        lines.append(f'{k} = "{val}"')
    return "\n".join(lines) + "\n" if lines else ""


def _format_backend_content(bucket_name: str, is_example: bool = False) -> str:
    """Formats backend.tfbackend content."""
    val = "" if is_example else bucket_name
    return f'bucket = "{val}"\n'


def synchronize_all(
    repo_root: str,
    dry_run: bool = False,
    validate_only: bool = False,
) -> Tuple[bool, List[str], List[str]]:
    """
    Synchronizes all environments and Terraform leaf modules.
    
    Returns:
    - success (bool): True if completed without errors (and in sync if validate_only).
    - changes_made (List[str]): List of human-readable descriptions of changes made or needed.
    - errors (List[str]): List of error messages encountered.
    """
    changes: List[str] = []
    errors: List[str] = []

    # Step 1: Pre-execution validation - Verify all .env files exist
    env_ok, missing_envs = validate_env_files_exist(repo_root)
    if not env_ok:
        err_msg = [
            "ERROR: Los siguientes archivos .env no existen:\n"
        ]
        for env_path, example_path in missing_envs:
            err_msg.append(f"   → {env_path}")
        err_msg.append("\n   Para crearlos, ejecute:")
        for env_path, example_path in missing_envs:
            err_msg.append(f"     cp {example_path}  {env_path}")
        err_msg.append("\n   Luego edite los valores y vuelva a ejecutar env-sync.")
        return False, [], ["\n".join(err_msg)]

    # Step 2: Iterate over scopes
    for scope_entry in SCOPE_MAP:
        scope_name = scope_entry["scope_name"]
        parent_rel = scope_entry["parent_dir"]
        env_rel = scope_entry["env_file"]

        parent_abs = os.path.join(repo_root, parent_rel)
        env_abs = os.path.join(repo_root, env_rel)

        if not os.path.isdir(parent_abs):
            continue

        # Autodiscover leaf modules
        leaf_tokens, intermediate_map = discover_leaf_modules(parent_abs)
        if not leaf_tokens:
            continue

        # Parse .env file
        try:
            modules_data = parse_env_file(env_abs, leaf_tokens, intermediate_map)
        except (SyntaxError, LexicalError, FileNotFoundError) as e:
            errors.append(str(e))
            continue

        # Step 3: Process each leaf module in the scope
        for mod_token in leaf_tokens:
            mod_abs_path = os.path.join(parent_abs, mod_token.replace("/", os.sep))
            mod_display_path = f"{parent_rel}/{mod_token}"

            mod_env = modules_data.get(mod_token, {"input_vars": {}, "backend_vars": {}})
            env_input_vars: Dict[str, str] = mod_env["input_vars"]
            env_backend_vars: Dict[str, str] = mod_env["backend_vars"]

            # --- A. Check variables.tf ---
            variables_tf_path = os.path.join(mod_abs_path, "variables.tf")
            existing_declared_vars = set(parse_variables_tf(variables_tf_path))

            # Union of all variables that should be declared
            all_target_vars: Set[str] = set(env_input_vars.keys())

            # Check if any env variable is missing in variables.tf
            missing_in_var_tf = all_target_vars - existing_declared_vars
            if missing_in_var_tf:
                new_declarations = []
                for var_name in sorted(missing_in_var_tf):
                    new_declarations.append(
                        f'\nvariable "{var_name}" {{\n'
                        f'  type        = string\n'
                        f'  description = "Synchronized via env-sync"\n'
                        f'}}\n'
                    )
                changes.append(f"[CREATE/UPDATE] {mod_display_path}/variables.tf: Added declarations for {sorted(missing_in_var_tf)}")
                if not dry_run and not validate_only:
                    with open(variables_tf_path, "a", encoding="utf-8") as f:
                        f.writelines(new_declarations)

            # --- B. Check terraform.tfvars ---
            tfvars_path = os.path.join(mod_abs_path, "terraform.tfvars")
            existing_tfvars = parse_tfvars_file(tfvars_path)

            # Desired tfvars: effective values from .env
            desired_tfvars = dict(existing_tfvars)
            desired_tfvars.update(env_input_vars)

            new_tfvars_content = _format_tfvars_content(desired_tfvars, is_example=False)
            current_tfvars_content = ""
            if os.path.isfile(tfvars_path):
                with open(tfvars_path, "r", encoding="utf-8") as f:
                    current_tfvars_content = f.read()

            if current_tfvars_content.strip() != new_tfvars_content.strip():
                action = "CREATE" if not os.path.isfile(tfvars_path) else "UPDATE"
                changes.append(f"[{action}] {mod_display_path}/terraform.tfvars")
                if not dry_run and not validate_only:
                    with open(tfvars_path, "w", encoding="utf-8") as f:
                        f.write(new_tfvars_content)

            # --- C. Check terraform.tfvars.example ---
            tfvars_example_path = os.path.join(mod_abs_path, "terraform.tfvars.example")
            new_example_content = _format_tfvars_content(desired_tfvars, is_example=True)
            current_example_content = ""
            if os.path.isfile(tfvars_example_path):
                with open(tfvars_example_path, "r", encoding="utf-8") as f:
                    current_example_content = f.read()

            if current_example_content.strip() != new_example_content.strip():
                action = "CREATE" if not os.path.isfile(tfvars_example_path) else "UPDATE"
                changes.append(f"[{action}] {mod_display_path}/terraform.tfvars.example")
                if not dry_run and not validate_only:
                    with open(tfvars_example_path, "w", encoding="utf-8") as f:
                        f.write(new_example_content)

            # --- D. Check backend.tfbackend (only if module has S3 backend) ---
            if has_s3_backend(mod_abs_path):
                bucket_val = (
                    env_backend_vars.get("terraform_state_bucket")
                    or env_backend_vars.get("bucket")
                    or ""
                )

                # backend.tfbackend
                backend_path = os.path.join(mod_abs_path, "backend.tfbackend")
                new_backend_content = _format_backend_content(bucket_val, is_example=False)
                current_backend_content = ""
                if os.path.isfile(backend_path):
                    with open(backend_path, "r", encoding="utf-8") as f:
                        current_backend_content = f.read()

                if current_backend_content.strip() != new_backend_content.strip():
                    action = "CREATE" if not os.path.isfile(backend_path) else "UPDATE"
                    changes.append(f"[{action}] {mod_display_path}/backend.tfbackend")
                    if not dry_run and not validate_only:
                        with open(backend_path, "w", encoding="utf-8") as f:
                            f.write(new_backend_content)

                # backend.tfbackend.example
                backend_example_path = os.path.join(mod_abs_path, "backend.tfbackend.example")
                new_backend_example_content = _format_backend_content(bucket_val, is_example=True)
                current_backend_example_content = ""
                if os.path.isfile(backend_example_path):
                    with open(backend_example_path, "r", encoding="utf-8") as f:
                        current_backend_example_content = f.read()

                if current_backend_example_content.strip() != new_backend_example_content.strip():
                    action = "CREATE" if not os.path.isfile(backend_example_path) else "UPDATE"
                    changes.append(f"[{action}] {mod_display_path}/backend.tfbackend.example")
                    if not dry_run and not validate_only:
                        with open(backend_example_path, "w", encoding="utf-8") as f:
                            f.write(new_backend_example_content)

    if errors:
        return False, changes, errors

    if validate_only:
        # If validate_only is True, return success=True only if 0 changes were needed
        is_synced = len(changes) == 0
        return is_synced, changes, []

    return True, changes, []
