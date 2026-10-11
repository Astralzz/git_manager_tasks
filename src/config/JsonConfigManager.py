import json
import os
import re
import sys
from typing import Any, Dict, List

from src.consts.env import BASE_PATH
from src.core.GlobalClass import GlobalClass
from src.types.configTypes import ExtendedConfigType


class JsonConfigManager(GlobalClass):
    """Carga repositorios y selecciona flujos o ramas de trabajo."""

    def __init__(self, json_file: str):
        super().__init__()
        self.json_file = json_file
        self.data: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        self.colors.info(f"Archivo de configuración: {self.json_file}")
        self.validate_required_fields([], self.json_file)

        try:
            with open(self.json_file, "r", encoding="utf-8") as config_file:
                self.data = json.load(config_file)
        except (json.JSONDecodeError, OSError) as error:
            self.colors.error(f"No se pudo leer la configuración: {error}")
            sys.exit(1)

        required = ("repo_roots", "branch_types", "areas")
        missing = [key for key in required if not self.data.get(key)]
        if missing:
            self.colors.error(
                f"Faltan secciones requeridas en config.json: {', '.join(missing)}"
            )
            sys.exit(1)
        return self.data

    def get_full_config_flow(self) -> ExtendedConfigType:
        """Selecciona área, proyecto y un flujo o nombre de rama."""
        self.load_config()

        area = self._select_item("ÁREAS", self.data["areas"])
        group = self._select_item(f"GRUPOS EN {area['name']}", area.get("groups", []))
        project = self._select_item(
            f"PROYECTOS EN {group['name']}", group.get("projects", [])
        )
        branch_types = self.data["branch_types"]
        presets = project.get("branches", [])
        branch_choices = [("new", None, "Nueva rama (defecto, issue o trabajo puntual)")]
        branch_choices.extend(
            ("preset", preset, preset.get("name", preset.get("id", "Rama configurada")))
            for preset in presets
        )
        choice_type, preset, _ = self._select_item(
            f"RAMAS EN {project['name']}",
            branch_choices,
            label=lambda item: item[2],
        )

        if choice_type == "new":
            branch_type, branch_definition = self._select_new_branch_type(
                project, branch_types
            )
            branch_slug = self._prompt_branch_slug(branch_definition)
            base_branch = self._select_new_branch_base(project, branch_type)
            branch_id = branch_slug
            branch_label = branch_slug
        else:
            branch_type, branch_config = self._select_preset_branch_type(
                preset, branch_types
            )
            branch_definition = branch_types[branch_type]
            branch_slug = self._resolve_preset_slug(
                branch_type, preset, branch_types
            )
            try:
                base_branch = self._resolve_base_branch(
                    branch_config.get("base", ""), preset, branch_types
                )
            except ValueError as error:
                self.colors.error(str(error))
                sys.exit(1)
            branch_id = preset.get("id", branch_slug)
            branch_label = preset.get("name", branch_id)

        prefix = branch_definition.get("prefix", "")
        target_branch = f"{prefix}{branch_slug}"
        repo_root_key = project.get("root", group.get("root", area.get("root")))
        repo_root = self.data["repo_roots"].get(repo_root_key)
        if not repo_root:
            self.colors.error(f"No existe la ruta raíz '{repo_root_key}' en repo_roots.")
            sys.exit(1)

        repo_path = self._resolve_repo_path(repo_root, project.get("folder", "."))
        if not base_branch or not target_branch:
            self.colors.error("Falta la rama base o el nombre de la rama destino.")
            sys.exit(1)

        selected: ExtendedConfigType = {
            "id": branch_id,
            "name": branch_label,
            "task": branch_id,
            "project": project.get("name", project.get("id", "")),
            "section": f"{area.get('name', '')} / {group.get('name', '')}".strip(" /"),
            "repo_path": repo_path,
            "base_branch": base_branch,
            "feature_branch": target_branch,
            "branch_type": branch_type,
            "branch_type_label": branch_type.upper(),
            "branch_environment": branch_definition.get("environment", ""),
        }

        self.view_selected_config(selected)
        if not self.confirm_action("¿La configuración seleccionada es correcta?"):
            sys.exit(1)
        return selected

    def _select_new_branch_type(
        self, project: Dict[str, Any], branch_types: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        defaults = project.get("branch_base_defaults", {})
        preferred_order = ["feature", "hotfix", "release"]
        type_order = [name for name in preferred_order if name in defaults]
        type_order.extend(name for name in defaults if name not in type_order)
        options = [
            (branch_type, branch_types[branch_type])
            for branch_type in type_order
            if branch_type in branch_types
        ]
        branch_type, definition = self._select_item(
            "TIPO PARA LA RAMA NUEVA",
            options,
            label=lambda item: (
                f"{item[0].upper()} → {item[1].get('environment', '')} "
                f"(base: {self._base_label(defaults[item[0]])})"
            ),
        )
        return branch_type, definition

    def _select_preset_branch_type(
        self, preset: Dict[str, Any], branch_types: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        configured = preset.get("types", {})
        options = []
        for branch_type, branch_config in configured.items():
            definition = branch_types.get(branch_type)
            if definition:
                try:
                    slug = self._resolve_preset_slug(
                        branch_type, preset, branch_types
                    )
                except ValueError as error:
                    self.colors.error(str(error))
                    sys.exit(1)
                target = f"{definition.get('prefix', '')}{slug}"
                label = f"{branch_type.upper()} → {definition.get('environment', '')}: {target}"
                options.append((branch_type, branch_config, label))

        branch_type, branch_config, _ = self._select_item(
            f"TIPO DE RAMA PARA {preset.get('name', preset.get('id', ''))}",
            options,
            label=lambda item: item[2],
        )
        return branch_type, branch_config

    def _select_new_branch_base(self, project: Dict[str, Any], branch_type: str) -> str:
        base = project.get("branch_base_defaults", {}).get(branch_type, "")
        if isinstance(base, list):
            return self._select_item(
                f"RAMA BASE PARA {branch_type.upper()}",
                base,
                label=lambda item: item,
            )
        return base

    @staticmethod
    def _base_label(base: Any) -> str:
        return ", ".join(base) if isinstance(base, list) else str(base)

    def _prompt_branch_slug(self, branch_definition: Dict[str, Any]) -> str:
        prefix = branch_definition.get("prefix", "")
        while True:
            try:
                prompt = (
                    f"Nombre/sufijo de la rama (sin '{prefix}' si ya tiene prefijo): "
                    if prefix
                    else "Nombre de la rama: "
                )
                slug = input(prompt).strip()
            except KeyboardInterrupt:
                self.colors.info("\nOperación cancelada.")
                sys.exit(0)

            if prefix and slug.startswith(prefix):
                slug = slug[len(prefix):]
            if self._is_valid_branch_slug(slug):
                return slug
            self.colors.error(
                "Usa letras, números, guiones, puntos o '/', sin espacios ni símbolos de shell."
            )

    @staticmethod
    def _is_valid_branch_slug(slug: str) -> bool:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", slug):
            return False
        if ".." in slug or "//" in slug or "@{" in slug or slug.endswith(("/", ".")):
            return False
        return all(
            segment
            and not segment.startswith(".")
            and not segment.lower().endswith(".lock")
            for segment in slug.split("/")
        )

    def _select_item(
        self,
        title: str,
        items: List[Any],
        label=lambda item: item.get("name", item.get("id", "")),
    ) -> Any:
        if not items:
            self.colors.error(f"No hay opciones disponibles en {title.lower()}.")
            sys.exit(1)

        self.colors.info("\n" + "=" * 60)
        self.colors.info(title)
        self.colors.info("=" * 60)
        for index, item in enumerate(items, start=1):
            self.colors.info(f"{index}. {label(item)}")

        while True:
            try:
                choice = int(input("Selecciona una opción: ").strip())
                if 1 <= choice <= len(items):
                    return items[choice - 1]
                self.colors.error(f"Elige un número entre 1 y {len(items)}.")
            except ValueError:
                self.colors.error("Introduce un número válido.")
            except KeyboardInterrupt:
                self.colors.info("\nOperación cancelada.")
                sys.exit(0)

    @staticmethod
    def _resolve_base_branch(
        base: str, preset: Dict[str, Any], branch_types: Dict[str, Any]
    ) -> str:
        """Resuelve una base literal o la rama de otro tipo del mismo flujo."""
        preset_branches = preset.get("types", {})
        if base in branch_types and base not in preset_branches:
            raise ValueError(f"El flujo no define la rama base '{base}'.")
        if base in preset_branches:
            base_definition = branch_types[base]
            base_slug = JsonConfigManager._resolve_preset_slug(
                base, preset, branch_types
            )
            return f"{base_definition.get('prefix', '')}{base_slug}"
        return base

    @staticmethod
    def _resolve_preset_slug(
        branch_type: str,
        preset: Dict[str, Any],
        branch_types: Dict[str, Any],
        trail: List[str] | None = None,
    ) -> str:
        """Hereda el slug de la base del flujo y agrega el sufijo configurado."""
        trail = trail or []
        if branch_type in trail:
            raise ValueError(
                f"Las ramas del flujo '{preset.get('name', preset.get('id', ''))}' "
                "tienen una dependencia circular."
            )

        branch_config = preset.get("types", {}).get(branch_type)
        if not branch_config:
            raise ValueError(f"El flujo no define el tipo de rama '{branch_type}'.")
        if branch_config.get("slug"):
            return branch_config["slug"]

        base = branch_config.get("base", "")
        parent_slug = preset.get("slug", "")
        if base in preset.get("types", {}):
            parent_slug = JsonConfigManager._resolve_preset_slug(
                base, preset, branch_types, [*trail, branch_type]
            )
        return f"{parent_slug}{branch_config.get('suffix', '')}"

    @staticmethod
    def _resolve_repo_path(root: str, folder: str) -> str:
        def has_windows_drive(path: str) -> bool:
            return len(path) >= 2 and path[1] == ":"

        if os.path.isabs(root) or has_windows_drive(root):
            full_path = os.path.join(root, folder)
        else:
            full_path = os.path.join(BASE_PATH, root, folder)
        return os.path.normpath(full_path).replace("\\", "/")


# Alias retained for main.py and existing imports.
JsonClass = JsonConfigManager
