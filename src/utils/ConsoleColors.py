from colorama import init, Fore, Style


# Clase para manejar los colores de la consola
class ConsoleColors:
    def __init__(self):
        # Inicializa colorama (para Windows)
        init(autoreset=True)

    # Función para imprimir un mensaje de error
    def error(self, message: str) -> None:
        print(Fore.RED + "❌ " + message + Style.RESET_ALL)

    # Función para imprimir un mensaje de éxito
    def success(self, message: str) -> None:
        print(Fore.GREEN + "✅ " + message + Style.RESET_ALL)

    # Función para imprimir un mensaje de advertencia
    def warning(self, message: str) -> None:
        print(Fore.YELLOW + "⚠ " + message + Style.RESET_ALL)

    # Función para imprimir un mensaje de información
    def info(self, message: str) -> None:
        print(Fore.CYAN + "ℹ " + message + Style.RESET_ALL)
