from src.git.GitClass import GitClass
from src.config.JsonConfigManager import JsonClass
from src.consts.env import CONFIG_FILE

# Función principal
def main():
    try:
        
        # Message de inicio
        print("\nIniciando al Gestor de Repositorios Git...\n")
                
        # Carga las configuraciones del json
        json_manager = JsonClass(CONFIG_FILE)
        
        # Flujo nuevo: Selecciona sección -> Selecciona config
        selected_config = json_manager.get_full_config_flow()

        # Configura git
        git_manager = GitClass(selected_config)

        # Muestra el menu de git
        git_manager.display_git_menu()
        
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. ¡Hasta luego!")
        return

# Ejecuta el programa
if __name__ == "__main__":
    main()
