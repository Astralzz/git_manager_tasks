import json
import sys
from typing import Dict, List

from src.consts.env import BASE_PATH
from src.core.GlobalClass import GlobalClass
from src.types.configTypes import ExtendedConfigType, ConfigSection


class JsonConfigManager(GlobalClass):
    """Clase para manejar la configuración JSON con secciones"""

    def __init__(self, json_file: str):
        """
        Inicializa el gestor de configuración JSON
        
        Args:
            json_file: Ruta al archivo de configuración
        """
        super().__init__()
        self.json_file = json_file
        self.sections_data: Dict[str, ConfigSection] = {}
        self.current_section: str = ""

    def load_sections(self) -> Dict[str, ConfigSection]:
        """
        Carga las secciones del archivo de configuración
        
        Returns:
            Diccionario con las secciones disponibles
        """
        self.colors.info(f"📁 Archivo de configuración: {self.json_file}")
        
        self.validate_required_fields([], self.json_file)
        
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.sections_data = data.get("sections", {})
            
        if not self.sections_data:
            self.colors.error("No se encontraron secciones en el archivo de configuración")
            sys.exit(1)
            
        return self.sections_data

    def select_section(self) -> str:
        """
        Permite seleccionar una sección
        
        Returns:
            La clave de la sección seleccionada
        """
        self.colors.info("\n" + "=" * 60)
        self.colors.info("📦 SECCIONES DISPONIBLES")
        self.colors.info("=" * 60)
        
        sections_list = list(self.sections_data.keys())
        
        for idx, (section_key, section_data) in enumerate(self.sections_data.items(), 1):
            description = section_data.get("description", "Sin descripción")
            config_count = len(section_data.get("configs", []))
            self.colors.info(f"{idx}. {description}")
            self.colors.info(f"   └─ {config_count} configuración(es) disponible(s)")
            self.colors.info("")
        
        self.colors.info("=" * 60)
        
        while True:
            try:
                selected = input("👉 Selecciona el número de la sección: ").strip()
                section_idx = int(selected) - 1
                
                if 0 <= section_idx < len(sections_list):
                    self.current_section = sections_list[section_idx]
                    section_info = self.sections_data[self.current_section]
                    self.colors.success(f"✅ Sección seleccionada: {section_info.get('description')}")
                    return self.current_section
                else:
                    self.colors.error("Número inválido. Intenta de nuevo.")
            except ValueError:
                self.colors.error("Debes introducir un número válido.")
            except KeyboardInterrupt:
                self.colors.info("\n\nOperación cancelada.")
                sys.exit(0)

    def view_section_configs(self, section_key: str) -> None:
        """
        Muestra las configuraciones de una sección
        
        Args:
            section_key: Clave de la sección
        """
        section = self.sections_data.get(section_key, {})
        configs = section.get("configs", [])
        
        if not configs:
            self.colors.warning("No hay configuraciones en esta sección.")
            return
        
        self.colors.info("\n" + "=" * 60)
        self.colors.info(f"📋 CONFIGURACIONES EN: {section.get('description')}")
        self.colors.info("=" * 60)
        
        for config in configs:
            self.colors.info(
                f"{config.get('number')}. {config.get('name')}"
            )
            self.colors.info(f"   ID: {config.get('id')}")
            self.colors.info(f"   Proyecto: {config.get('project')}")
            self.colors.info(f"   Task: {config.get('task')}")
            self.colors.info(f"   Base: {config.get('base_branch')} → Feature: {config.get('feature_branch')}")
            self.colors.info("")

    def select_config_from_section(self, section_key: str) -> ExtendedConfigType:
        """
        Selecciona una configuración de la sección actual
        
        Args:
            section_key: Clave de la sección
            
        Returns:
            La configuración seleccionada con ruta completa
        """
        section = self.sections_data.get(section_key, {})
        configs = section.get("configs", [])
        
        if not configs:
            self.colors.error("No hay configuraciones disponibles en esta sección.")
            sys.exit(1)
        
        self.view_section_configs(section_key)
        
        self.colors.info("=" * 60)
        
        while True:
            try:
                selected = input("👉 Selecciona el número de la configuración: ").strip()
                selected_num = int(selected)
                
                for config in configs:
                    if config.get("number") == selected_num:
                        return self._prepare_config(config, section_key)
                
                self.colors.error(f"No se encontró una configuración con el número '{selected_num}'")
            except ValueError:
                self.colors.error("Debes introducir un número válido.")
            except KeyboardInterrupt:
                self.colors.info("\n\nOperación cancelada.")
                sys.exit(0)

    def _prepare_config(self, config: Dict, section_key: str) -> ExtendedConfigType:
        """
        Prepara la configuración con la ruta completa y metadata adicional
        
        Args:
            config: Configuración base
            section_key: Clave de la sección
            
        Returns:
            Configuración extendida con toda la información necesaria
        """
        import os
        
        repo_value = config.get("repo_path")
        if not repo_value:
            self.colors.error("La configuración no contiene un valor válido para 'repo_path'.")
            sys.exit(1)
        
        section_description = self.sections_data[section_key].get("description", section_key)
        
        # Crear configuración con tipo correcto
        config_with_path = {
            **config,
            "repo_path": os.path.join(BASE_PATH, repo_value),
            "section": section_description,
        }
        
        self.view_selected_config(config_with_path)  # type: ignore
        
        if not self.confirm_action("¿La configuración seleccionada es correcta?"):
            sys.exit(1)
        
        return config_with_path  # type: ignore

    def get_full_config_flow(self) -> ExtendedConfigType:
        """
        Flujo completo: cargar secciones -> seleccionar sección -> seleccionar config
        
        Returns:
            La configuración final seleccionada
        """
        self.load_sections()
        section_key = self.select_section()
        return self.select_config_from_section(section_key)


# Alias para compatibilidad con código existente
JsonClass = JsonConfigManager
