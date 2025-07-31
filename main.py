import subprocess
import json
import os
import sys
from classes.GitClass import GitClass
from classes.JsonClass import JsonClass
from classes.ConsoleColors import ConsoleColors
from consts.env import CONFIG_FILE

# Funcion principal
def main():

    # Carga las configuraciones del json
    json_manager = JsonClass(CONFIG_FILE)
    configs = json_manager.load_configs()
    selected_config = json_manager.select_config(configs)

    # Configura git
    git_manager = GitClass(selected_config)
    
    # Muestra el menu de git
    git_manager.display_git_menu()


# Ejecuta el programa
if __name__ == "__main__":
    main()
