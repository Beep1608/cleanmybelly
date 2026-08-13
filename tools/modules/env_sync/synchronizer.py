"""
Synchronizer module for env-sync.
Calculates bidirectional and lateral diffs, applies precedence hierarchy,
and synchronizes all managed files across Terraform leaf modules, active .env files,
and .env.example blueprint templates.
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


def _inject_variables_into_env_file(
    env_file_path: str,
    module_token: str,
    new_vars: Dict[str, str],
    is_backend: bool = False,
) -> bool:
    """
    Injects or appends discovered variables under [module_token] in the specified .env or .example file.
    Preserves existing structure and comments. Returns True if modified.
    """
    if not new_vars or not os.path.isfile(env_file_path):
        return False

    with open(env_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Search for existing exact directive [module_token]
    target_section_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() == f"[{module_token}]":
            target_section_idx = idx
            break

    new_var_lines = []
    for k, v in sorted(new_vars.items()):
        prefix = "!" if (is_backend and not k.startswith("!")) else ""
        new_var_lines.append(f'{prefix}{k} = "{v}"\n')

    if target_section_idx != -1:
        # Find where this section ends (next directive line [ ... ] or EOF)
        insert_idx = len(lines)
        for idx in range(target_section_idx + 1, len(lines)):
            if lines[idx].strip().startswith("[") and lines[idx].strip().endswith("]"):
                insert_idx = idx
                break
        
        # Insert before next section
        lines[insert_idx:insert_idx] = new_var_lines
    else:
        # Append new section at the bottom
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.append(f"[{module_token}]\n")
        lines.extend(new_var_lines)

    with open(env_file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def synchronize_all(
    repo_root: str,
    dry_run: bool = False,
    validate_only: bool = False,
) -> Tuple[bool, List[str], List[str]]:
    """
    Synchronizes all environments, blueprints, and Terraform leaf modules in all directions (bidirectional + lateral).
    
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

    # Step 2: Pass 1 - Lateral Synchronization (.env <-> .env.example)
    for scope_entry in SCOPE_MAP:
        parent_rel = scope_entry["parent_dir"]
        env_rel = scope_entry["env_file"]
        example_rel = scope_entry["example_file"]

        parent_abs = os.path.join(repo_root, parent_rel)
        env_abs = os.path.join(repo_root, env_rel)
        example_abs = os.path.join(repo_root, example_rel)

        if not os.path.isdir(parent_abs) or not os.path.isfile(env_abs):
            continue

        leaf_tokens, intermediate_map = discover_leaf_modules(parent_abs)
        if not leaf_tokens:
            continue

        # Parse .env
        try:
            env_data = parse_env_file(env_abs, leaf_tokens, intermediate_map)
        except (SyntaxError, LexicalError, FileNotFoundError) as e:
            errors.append(str(e))
            continue

        # Parse .env.example if exists
        example_data = {}
        if os.path.isfile(example_abs):
            try:
                example_data = parse_env_file(example_abs, leaf_tokens, intermediate_map)
            except (SyntaxError, LexicalError) as e:
                errors.append(str(e))
                continue

        # Propagate from .env to .env.example
        for mod_token in leaf_tokens:
            env_inputs = env_data.get(mod_token, {}).get("input_vars", {})
            env_backends = env_data.get(mod_token, {}).get("backend_vars", {})
            
            ex_inputs = example_data.get(mod_token, {}).get("input_vars", {})
            ex_backends = example_data.get(mod_token, {}).get("backend_vars", {})

            # Missing input vars in .example
            missing_in_example = set(env_inputs.keys()) - set(ex_inputs.keys())
            if missing_in_example:
                inject_ex = {k: "" for k in sorted(missing_in_example)}
                changes.append(
                    f"[LATERAL-SYNC] {example_rel}: Injected template for {sorted(missing_in_example)} under [{mod_token}]"
                )
                if not dry_run and not validate_only:
                    _inject_variables_into_env_file(example_abs, mod_token, inject_ex, is_backend=False)

            # Missing backend vars in .example
            missing_be_in_example = set(env_backends.keys()) - set(ex_backends.keys())
            if missing_be_in_example:
                inject_be_ex = {k: "" for k in sorted(missing_be_in_example)}
                changes.append(
                    f"[LATERAL-SYNC] {example_rel}: Injected backend template for {sorted(missing_be_in_example)} under [{mod_token}]"
                )
                if not dry_run and not validate_only:
                    _inject_variables_into_env_file(example_abs, mod_token, inject_be_ex, is_backend=True)

            # Missing input vars in .env (if someone added to .example first)
            missing_in_env = set(ex_inputs.keys()) - set(env_inputs.keys())
            if missing_in_env:
                inject_env = {k: ex_inputs.get(k, "") for k in sorted(missing_in_env)}
                changes.append(
                    f"[LATERAL-SYNC] {env_rel}: Discovered {sorted(missing_in_env)} from {example_rel} and added under [{mod_token}]"
                )
                if not dry_run and not validate_only:
                    _inject_variables_into_env_file(env_abs, mod_token, inject_env, is_backend=False)

    # Step 3: Pass 2 - Reverse Synchronization (Modules -> .env & .env.example)
    for scope_entry in SCOPE_MAP:
        parent_rel = scope_entry["parent_dir"]
        env_rel = scope_entry["env_file"]
        example_rel = scope_entry["example_file"]

        parent_abs = os.path.join(repo_root, parent_rel)
        env_abs = os.path.join(repo_root, env_rel)
        example_abs = os.path.join(repo_root, example_rel)

        if not os.path.isdir(parent_abs) or not os.path.isfile(env_abs):
            continue

        leaf_tokens, intermediate_map = discover_leaf_modules(parent_abs)
        if not leaf_tokens:
            continue

        try:
            modules_data = parse_env_file(env_abs, leaf_tokens, intermediate_map)
        except (SyntaxError, LexicalError, FileNotFoundError) as e:
            errors.append(str(e))
            continue

        for mod_token in leaf_tokens:
            mod_abs_path = os.path.join(parent_abs, mod_token.replace("/", os.sep))
            mod_display_path = f"{parent_rel}/{mod_token}"

            mod_env = modules_data.get(mod_token, {"input_vars": {}, "backend_vars": {}})
            known_env_input_vars = set(mod_env["input_vars"].keys())

            # Read variables declared in variables.tf
            variables_tf_path = os.path.join(mod_abs_path, "variables.tf")
            local_declared_vars = set(parse_variables_tf(variables_tf_path))

            # Variables declared in variables.tf but missing in .env
            missing_in_env = local_declared_vars - known_env_input_vars

            if missing_in_env:
                tfvars_path = os.path.join(mod_abs_path, "terraform.tfvars")
                local_tfvars = parse_tfvars_file(tfvars_path)

                new_vars_for_env = {}
                new_vars_for_example = {}
                for var_name in sorted(missing_in_env):
                    val = local_tfvars.get(var_name, "")
                    new_vars_for_env[var_name] = val
                    new_vars_for_example[var_name] = ""

                changes.append(
                    f"[REVERSE-SYNC] {env_rel}: Discovered {sorted(missing_in_env)} in {mod_display_path}/variables.tf and added under [{mod_token}]"
                )
                changes.append(
                    f"[LATERAL-SYNC] {example_rel}: Injected template for {sorted(missing_in_env)} under [{mod_token}]"
                )

                if not dry_run and not validate_only:
                    _inject_variables_into_env_file(env_abs, mod_token, new_vars_for_env, is_backend=False)
                    if os.path.isfile(example_abs):
                        _inject_variables_into_env_file(example_abs, mod_token, new_vars_for_example, is_backend=False)

    # Step 4: Pass 3 - Forward Synchronization (.env -> all module files)
    for scope_entry in SCOPE_MAP:
        scope_name = scope_entry["scope_name"]
        parent_rel = scope_entry["parent_dir"]
        env_rel = scope_entry["env_file"]

        parent_abs = os.path.join(repo_root, parent_rel)
        env_abs = os.path.join(repo_root, env_rel)

        if not os.path.isdir(parent_abs) or not os.path.isfile(env_abs):
            continue

        leaf_tokens, intermediate_map = discover_leaf_modules(parent_abs)
        if not leaf_tokens:
            continue

        # Re-parse .env file to get latest variables after reverse and lateral sync
        try:
            modules_data = parse_env_file(env_abs, leaf_tokens, intermediate_map)
        except (SyntaxError, LexicalError, FileNotFoundError) as e:
            errors.append(str(e))
            continue

        for mod_token in leaf_tokens:
            mod_abs_path = os.path.join(parent_abs, mod_token.replace("/", os.sep))
            mod_display_path = f"{parent_rel}/{mod_token}"

            mod_env = modules_data.get(mod_token, {"input_vars": {}, "backend_vars": {}})
            env_input_vars: Dict[str, str] = mod_env["input_vars"]
            env_backend_vars: Dict[str, str] = mod_env["backend_vars"]

            # --- A. Check variables.tf ---
            variables_tf_path = os.path.join(mod_abs_path, "variables.tf")
            existing_declared_vars = set(parse_variables_tf(variables_tf_path))
            all_target_vars: Set[str] = set(env_input_vars.keys())

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
            desired_tfvars = dict(env_input_vars)

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
