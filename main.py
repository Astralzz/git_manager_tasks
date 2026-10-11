from src.utils.ExceptionsClass import RestartProgramException
from src.git.GitClass import GitClass
from src.config.JsonConfigManager import JsonClass
from src.consts.env import CONFIG_FILE


def main():
    while True:
        try:
            print("\nIniciando al Gestor de Repositorios Git...\n")
            json_manager = JsonClass(CONFIG_FILE)
            selected_config = json_manager.get_full_config_flow()
            git_manager = GitClass(selected_config)
            git_manager.display_git_menu()
            return

        except RestartProgramException:
            print("\nVolviendo al selector de proyectos...")
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido por el usuario. Hasta luego.")
            return
        except SystemExit as error:
            if error.code in (None, 0):
                return
            print(
                f"\nLa operacion termino con error (codigo {error.code}). "
                "Volviendo al selector de proyectos..."
            )
        except Exception as error:
            print(
                f"\nError inesperado ({type(error).__name__}): {error}"
                "\nVolviendo al selector de proyectos..."
            )


if __name__ == "__main__":
    main()