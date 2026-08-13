#!/usr/bin/env python3
"""
env-sync: CLI tool for deterministic Terraform environment and variable synchronization.

Usage:
  python3 tools/env_sync.py                 # Full automatic synchronization
  python3 tools/env_sync.py --dry-run       # Preview changes without modifying files
  python3 tools/env_sync.py --validate      # Validate consistency (exit 0 = OK, exit 1 = desynced)
"""

import sys
import argparse
from modules.env_sync import get_repo_root, synchronize_all


def main() -> int:
    parser = argparse.ArgumentParser(
        description="env-sync: Deterministic Terraform environment and variable synchronization tool."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes that would be made without writing to disk.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Check if all managed files are in sync. Exits with 0 if synced, 1 if desynchronized.",
    )

    args = parser.parse_args()
    repo_root = get_repo_root()

    print("=" * 70)
    print(" 🔄 env-sync: Terraform Environment & Variable Synchronizer")
    print("=" * 70)

    if args.validate:
        print(" Modo: VALIDATE (verificación de consistencia sin modificar archivos)\n")
    elif args.dry_run:
        print(" Modo: DRY-RUN (previsualización de cambios sin escribir a disco)\n")
    else:
        print(" Modo: SYNC (sincronización y creación automática de archivos)\n")

    success, changes, errors = synchronize_all(
        repo_root=repo_root,
        dry_run=args.dry_run,
        validate_only=args.validate,
    )

    if errors:
        print("\n❌ ERRORES DETECTADOS:")
        for err in errors:
            print(f"  {err}")
        print("=" * 70)
        return 1

    if args.validate:
        if success:
            print("✅ Todos los módulos de Terraform y archivos .env están 100% sincronizados.")
            print("=" * 70)
            return 0
        else:
            print("⚠️ DESINCRONIZACIÓN DETECTADA: Se requieren los siguientes cambios:\n")
            for change in changes:
                print(f"  • {change}")
            print("\nPara sincronizar, ejecute: python3 tools/env_sync.py")
            print("=" * 70)
            return 1

    if changes:
        action_verb = "Cambios a aplicar (Dry-Run)" if args.dry_run else "Cambios aplicados exitosamente"
        print(f"📋 {action_verb} ({len(changes)} operaciones):\n")
        for change in changes:
            print(f"  • {change}")
    else:
        print("✨ Todos los archivos ya se encuentran al día. Cero modificaciones requeridas.")

    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
