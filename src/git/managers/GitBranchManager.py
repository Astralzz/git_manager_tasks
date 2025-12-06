import sys
from typing import Optional, List, TYPE_CHECKING
from colorama import Fore

if TYPE_CHECKING:
    from src.types.configTypes import GitCommandResult


class GitBranchManager:
    """Clase para manejar operaciones relacionadas con ramas Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de ramas con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger
        self.base_branch = git_instance.base_branch
        self.feature_branch = git_instance.feature_branch

    def validate_branch_configuration(self) -> None:
        """Valida que la configuración de ramas sea correcta"""
        if not self.feature_branch:
            self.colors.error("La rama feature no está configurada.")
            sys.exit(1)

        if not self.base_branch:
            self.colors.error("La rama base no está configurada.")
            sys.exit(1)

        if self.feature_branch.lower() in ["main", "master"]:
            self.colors.error(f"La rama feature no puede ser '{self.feature_branch}'.")
            if hasattr(self.git, "logger"):
                self.git_logger.log_error(
                    f"Configuración inválida: feature_branch = {self.feature_branch}",
                    "_validate_branch_configuration",
                )
            sys.exit(1)

        if self.base_branch == self.feature_branch:
            self.colors.error("La rama base y la rama feature no pueden ser iguales.")
            if hasattr(self.git, "logger"):
                self.git_logger.log_error(
                    "Configuración inválida: base_branch == feature_branch",
                    "_validate_branch_configuration",
                )
            sys.exit(1)

    def auto_checkout_to_feature_branch(self) -> None:
        """Intenta cambiar automáticamente a la rama feature configurada"""
        try:
            result = self.git.run_git_command(
                "git branch --show-current", allow_failure=True
            )
            current_branch = result["stdout"].strip()

            target_branch = self.feature_branch.strip() if self.feature_branch else ""

            if current_branch == target_branch:
                self.colors.success(
                    f"Ya estás en la rama feature: {Fore.YELLOW}{target_branch}{Fore.RESET}"
                )
                return

            check_local = self.git.run_git_command(
                f"git show-ref --verify --quiet refs/heads/{target_branch}",
                allow_failure=True,
            )

            if check_local["returncode"] == 0:
                self._checkout_existing_branch(current_branch, target_branch)
            else:
                self._check_remote_branch(current_branch)

        except Exception as e:
            self.colors.warning(f"Error al verificar rama: {str(e)}")
            self.colors.info(" El programa continuará normalmente.")

    def _checkout_existing_branch(self, current_branch: str, target_branch: str) -> None:
        """Hace checkout a una rama existente"""
        self.colors.info(
            f" Cambiando a la rama feature: {Fore.YELLOW}{target_branch}{Fore.RESET}"
        )
        checkout_result = self.git.run_git_command(
            f"git checkout {target_branch}", allow_failure=True
        )

        if checkout_result["returncode"] == 0:
            self.colors.success(
                f"Posicionado en la rama: {Fore.YELLOW}{target_branch}{Fore.RESET}"
            )
            self.git_logger.log_operation(
                "AUTO_CHECKOUT",
                f"Cambio automático a {target_branch}",
                "SUCCESS",
            )
        else:
            status_check = self.git.run_git_command("git status --porcelain", allow_failure=True)
            if status_check["stdout"].strip():
                self._handle_checkout_with_changes(current_branch, target_branch, checkout_result)
            else:
                self.colors.warning(
                    f"No se pudo cambiar a la rama {target_branch}"
                )
                self.colors.error(f"Error específico: {checkout_result.get('stderr', 'Sin error específico')}")
                self.colors.info(
                    f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}"
                )
                
                self.git_logger.log_operation(
                    "AUTO_CHECKOUT",
                    f"Error al cambiar a {target_branch}: {checkout_result.get('stderr', '')}",
                    "ERROR",
                )

    def _handle_checkout_with_changes(self, current_branch: str, target_branch: str, checkout_result: "GitCommandResult") -> None:
        """Maneja el checkout cuando hay cambios locales pendientes"""
        self.colors.warning("Tienes cambios sin commitear que impiden el checkout:")
        self.git.run_git_command("git status --short")
        
        self.colors.info("\n Opciones disponibles:")
        self.colors.info("  1.  Guardar cambios temporalmente (stash) y cambiar de rama")
        self.colors.info("  2. 📍 Permanecer en la rama actual y continuar")
        self.colors.info("  3.  Ver detalles de los cambios antes de decidir")
        
        while True:
            try:
                choice = input("\n🔍 Selecciona una opción (1-3): ").strip()
                
                if choice == "1":
                    if self._stash_and_checkout(current_branch, target_branch):
                        return
                    else:
                        break
                        
                elif choice == "2":
                    self.colors.info(f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")
                    self.git_logger.log_operation(
                        "AUTO_CHECKOUT",
                        f"Usuario decidió permanecer en {current_branch}",
                        "INFO",
                    )
                    return
                    
                elif choice == "3":
                    self.colors.info(" Detalles de los cambios:")
                    self.git.run_git_command("git diff --name-status")
                    self.colors.info("\n Vista previa de cambios:")
                    self.git.run_git_command("git diff --stat")
                    continue
                    
                else:
                    self.colors.warning("Opción inválida. Selecciona 1, 2 o 3.")
                    continue
                    
            except KeyboardInterrupt:
                self.colors.info(f"\n📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")
                return
        
        self.colors.info(f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")

    def _stash_and_checkout(self, current_branch: str, target_branch: str) -> bool:
        """Guarda cambios con stash y hace checkout"""
        try:
            from src.git.managers.GitStashManager import GitStashManager
            stash_manager = GitStashManager(self.git)
            
            self.colors.info(" Guardando cambios temporalmente...")
            stash_manager.save_changes_locally()
            
            self.colors.info(f" Cambiando a {Fore.YELLOW}{target_branch}{Fore.RESET}...")
            checkout_result = self.git.run_git_command(
                f"git checkout {target_branch}", 
                allow_failure=True
            )
            
            if checkout_result["returncode"] == 0:
                self.colors.success(f"Posicionado en: {Fore.YELLOW}{target_branch}{Fore.RESET}")
                self.colors.info(f" Tus cambios están guardados en stash. Usa la opción del menú para restaurarlos.")
                
                self.git_logger.log_operation(
                    "AUTO_CHECKOUT_WITH_STASH",
                    f"Checkout exitoso a {target_branch} con stash",
                    "SUCCESS",
                )
                return True
            else:
                self.colors.error(" Error al cambiar de rama incluso después del stash")
                self.colors.info(" Restaurando cambios...")
                stash_manager.restore_local_changes()
                return False
                
        except Exception as e:
            self.colors.error(f" Error inesperado durante stash y checkout: {str(e)}")
            return False

    def _check_remote_branch(self, current_branch: str) -> None:
        """Verifica si la rama existe en remoto y la descarga si es posible"""
        check_remote = self.git.run_git_command(
            f"git ls-remote --heads origin {self.feature_branch}", allow_failure=True
        )

        if check_remote["stdout"].strip():
            self.colors.info(
                f" La rama {Fore.YELLOW}{self.feature_branch}{Fore.RESET} existe en remoto. Descargando..."
            )

            checkout_remote = self.git.run_git_command(
                f"git checkout -b {self.feature_branch} origin/{self.feature_branch}",
                allow_failure=True,
            )

            if checkout_remote["returncode"] == 0:
                self.colors.success(
                    f"Rama descargada y posicionado en: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                )
                self.git_logger.log_operation(
                    "AUTO_CHECKOUT_REMOTE",
                    f"Descarga y cambio a {self.feature_branch} desde remoto",
                    "SUCCESS",
                )
            else:
                track_result = self.git.run_git_command(
                    f"git checkout --track origin/{self.feature_branch}",
                    allow_failure=True,
                )
                if track_result["returncode"] == 0:
                    self.colors.success(
                        f"Rama rastreada: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                    )
                else:
                    self.colors.warning(f"No se pudo descargar la rama remota")
                    self.colors.info(
                        f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}"
                    )
        else:
            self._show_new_task_info(current_branch)

    def _show_new_task_info(self, current_branch: str) -> None:
        """Muestra información cuando se detecta una nueva tarea"""
        self.colors.info("━" * 60)
        self.colors.warning(" NUEVA TAREA DETECTADA")
        self.colors.info(
            f"   La rama {Fore.YELLOW}{self.feature_branch}{Fore.RESET} no existe aún."
        )
        self.colors.info(
            f"   Actualmente estás en: {Fore.CYAN}{current_branch}{Fore.RESET}"
        )
        self.colors.info(
            "   Usa la opción 6 del menú para crear la rama cuando estés listo."
        )
        self.colors.info("━" * 60)
        self.git_logger.log_operation(
            "NEW_TASK_DETECTED",
            f"Nueva tarea detectada: {self.feature_branch} no existe",
            "INFO",
        )

    def get_current_branch(self) -> None:
        """Muestra todas las ramas y marca la actual"""
        self.git.run_git_command("git branch")

    def create_branch_feature(self) -> None:
        """Crea una nueva rama feature desde la rama actual"""
        self.git.ask_pass()

        local_check = self.git.run_git_command(
            f"git rev-parse --verify --quiet {self.feature_branch}", allow_failure=True
        )

        if local_check["returncode"] == 0:
            self.colors.warning(
                f"La rama '{self.feature_branch}' ya existe localmente."
            )
            return

        remote_check = self.git.run_git_command(
            f"git ls-remote --heads origin {self.feature_branch}", allow_failure=True
        )

        if remote_check["stdout"].strip():
            self.colors.warning(
                f"La rama '{self.feature_branch}' ya existe en remoto."
            )
            self.colors.info(" Usa git checkout para cambiar a ella.")
            return

        self.colors.info(f" Creando nueva rama: {self.feature_branch}")
        create_result = self.git.run_git_command(
            f"git checkout -b {self.feature_branch}", allow_failure=True
        )

        if create_result["returncode"] == 0:
            self.colors.success(f"Rama '{self.feature_branch}' creada exitosamente.")
            self.git_logger.log_branch_operation(
                "create", self.feature_branch, "SUCCESS"
            )
        else:
            self.colors.error(
                f"Error al crear la rama: {create_result.get('stderr', '')}"
            )
            self.git_logger.log_branch_operation(
                "create", self.feature_branch, "ERROR"
            )

    def delete_branch(self) -> None:
        """Elimina una rama específica con menú interactivo"""
        self.git.ask_pass()

        branches_result = self.git.run_git_command("git branch", allow_failure=True)
        if branches_result["returncode"] != 0:
            self.colors.error("Error al obtener las ramas locales.")
            return

        all_branches: List[str] = []
        current_branch: str = ""

        for line in branches_result["stdout"].split("\n"):
            line = line.strip()
            if line:
                if line.startswith("* "):
                    current_branch = line[2:].strip()
                    all_branches.append(current_branch)
                else:
                    all_branches.append(line.strip())

        deletable_branches: List[str] = []
        protected_branches = ["main", "master", "develop", "development"]

        for branch in all_branches:
            if branch != current_branch and branch.lower() not in protected_branches:
                deletable_branches.append(branch)

        if not deletable_branches:
            self.colors.warning("No hay ramas disponibles para eliminar.")
            self.colors.info(f"📍 Rama actual: {Fore.CYAN}{current_branch}{Fore.RESET}")
            return

        self.colors.info("🗑️ SELECCIONAR RAMA PARA ELIMINAR")
        self.colors.info("━" * 50)
        self.colors.info(f"📍 Rama actual: {Fore.CYAN}{current_branch}{Fore.RESET}")
        self.colors.info("━" * 50)

        for i, branch in enumerate(deletable_branches, 1):
            self.colors.info(f"  {i}. {Fore.YELLOW}{branch}{Fore.RESET}")

        self.colors.info(
            f"  {len(deletable_branches) + 1}.  Escribir otra rama manualmente"
        )
        self.colors.info(f"  {len(deletable_branches) + 2}. Salir")
        self.colors.info("━" * 50)

        try:
            choice = input(" Selecciona una opción (número): ").strip()
            if not choice:
                self.colors.warning("No se seleccionó ninguna opción.")
                return

            choice_num = int(choice)

            if choice_num == len(deletable_branches) + 2:
                self.colors.info("Operación cancelada.")
                return

            elif choice_num == len(deletable_branches) + 1:
                branch_name = input(" Nombre de la rama a eliminar: ").strip()
                if not branch_name:
                    self.colors.warning(" No se especificó ninguna rama.")
                    return

            elif 1 <= choice_num <= len(deletable_branches):
                branch_name = deletable_branches[choice_num - 1]

            else:
                self.colors.error("Opción inválida.")
                return

        except ValueError:
            self.colors.error("Debes introducir un número válido.")
            return

        self.git_logger.log_user_input("branch_to_delete", branch_name)

        if branch_name == current_branch:
            self.colors.error("No puedes eliminar la rama en la que estás.")
            return

        if branch_name.lower() in protected_branches:
            if not self.git.confirm_action(
                f"'{branch_name}' es una rama protegida. ¿Seguro que deseas eliminarla?"
            ):
                return

        self.colors.warning(
            f"Vas a eliminar la rama: {Fore.YELLOW}{branch_name}{Fore.RESET}"
        )
        if not self.git.confirm_action("¿Continuar con la eliminación?"):
            self.colors.info("Eliminación cancelada.")
            return

        delete_result = self.git.run_git_command(
            f"git branch -D {branch_name}", allow_failure=True
        )

        if delete_result["returncode"] == 0:
            self.colors.success(f"Rama '{branch_name}' eliminada localmente.")
            self.colors.info(
                "Solo se eliminó la rama local, el remoto no fue afectado."
            )
            self.git_logger.log_branch_operation("delete", branch_name, "SUCCESS")
        else:
            self.colors.error(
                f"Error al eliminar la rama: {delete_result.get('stderr', '')}"
            )
            self.git_logger.log_branch_operation("delete", branch_name, "ERROR")
