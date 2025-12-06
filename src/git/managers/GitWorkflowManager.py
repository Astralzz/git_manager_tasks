from colorama import Fore
from src.consts.env import GIT_CONFIG_ID


class GitWorkflowManager:
    """Clase para manejar flujos complejos de Git (GitFlow, etc)"""

    def __init__(self, git_instance):
        """Inicializa el gestor de workflows con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger
        self.git_config = git_instance.git_config
        self.base_branch = git_instance.base_branch
        self.feature_branch = git_instance.feature_branch

    def feature_branch_workflow(self):
        """Flujo completo de feature branch según GitFlow CONACYT - Arquitectura GitFlow"""
        self.git.ask_pass()

        self.colors.info("\n=== FLUJO DE FEATURE BRANCH - CONACYT ===")

        if (
            self.feature_branch != "develop"
            or self.base_branch != "main"
            or not self.git_config
            or self.git_config.get("id") != GIT_CONFIG_ID
        ):
            self.colors.error(
                f"Este flujo solo es muy especifico y solo válido para: "
                f"'develop' con base 'main' y "
                f"configuración de ID única ?????."
            )
            return

        if not self.git.confirm_action(
            "Esto solo es para una tarea especifica, estas seguro?"
        ):
            self.colors.info("Operación cancelada.")
            return

        version = input("Ingresa la versión (ej: [N].[N].[N]): ").strip()
        if not version:
            self.colors.error("La versión es requerida")
            return

        message = input("Ingresa el mensaje del commit: ").strip()
        if not message:
            self.colors.error("El mensaje del commit es requerido")
            return

        feature_name = f"feature/version-{version.replace('.', '-')}"

        self.git_logger.log_user_input("version", version)
        self.git_logger.log_user_input("commit_message", message)
        self.git_logger.log_user_input("feature_name", feature_name)

        self.colors.info(
            f"\n🚀 Iniciando flujo: {Fore.YELLOW}{feature_name}{Fore.RESET}"
        )

        try:
            self.colors.info("\n📍 PASO 1: Actualizando rama develop...")

            checkout_result = self.git.run_git_command(
                "git checkout develop", allow_failure=True
            )
            if checkout_result["returncode"] != 0:
                self.colors.error("Error al cambiar a develop")
                return

            pull_result = self.git.run_git_command(
                "git pull origin develop", allow_failure=True
            )
            if pull_result[
                "returncode"
            ] != 0 and "Already up to date" not in pull_result.get("stdout", ""):
                self.colors.error("Error al actualizar develop")
                return

            self.colors.info(
                f"\n PASO 2: Creando rama {Fore.YELLOW}{feature_name}{Fore.RESET}..."
            )

            exists = self.git.run_git_command(
                f"git rev-parse --verify {feature_name}", allow_failure=True
            )
            if exists["returncode"] == 0:
                self.colors.warning(f"La rama {feature_name} ya existe")
                self.git.run_git_command(f"git checkout {feature_name}")
            else:
                create_result = self.git.run_git_command(
                    f"git checkout -b {feature_name}", allow_failure=True
                )
                if create_result["returncode"] != 0:
                    self.colors.error(f"Error al crear la rama {feature_name}")
                    return

            self.colors.info("\n💾 PASO 3: Realizando cambios y commit...")

            status = self.git.run_git_command("git status --porcelain", allow_failure=True)
            if not status["stdout"].strip():
                self.colors.warning("No hay cambios para commitear")
                if not self.git.confirm_action("¿Continuar sin cambios?"):
                    return
            else:
                self.colors.info(" Cambios detectados:")
                self.git.run_git_command("git status --short")

                self.colors.info("▶ Ejecutando: git add .")
                add_result = self.git.run_git_command("git add .", allow_failure=True)
                if add_result["returncode"] != 0:
                    self.colors.error("Error al añadir cambios")
                    return

                self.colors.info(f"▶ Ejecutando: git commit -m '{message}'")
                commit_result = self.git.run_git_command(
                    f'git commit -m "{message}"', allow_failure=True
                )
                if commit_result["returncode"] != 0:
                    if "nothing to commit" in commit_result.get("stdout", ""):
                        self.colors.warning("No hay cambios nuevos para commitear")
                    else:
                        self.colors.error("Error al hacer commit")
                        return
                else:
                    self.colors.success("Commit realizado exitosamente")

            self.colors.info("\n PASO 4: Volviendo a develop y actualizando...")

            checkout_dev = self.git.run_git_command(
                "git checkout develop", allow_failure=True
            )
            if checkout_dev["returncode"] != 0:
                self.colors.error("Error al cambiar a develop")
                return

            pull_dev = self.git.run_git_command(
                "git pull origin develop", allow_failure=True
            )
            if pull_dev["returncode"] != 0 and "Already up to date" not in pull_dev.get(
                "stdout", ""
            ):
                self.colors.warning("Advertencia al actualizar develop")

            self.colors.info(
                f"Haciendo merge de {Fore.YELLOW}{feature_name}{Fore.RESET}..."
            )
            merge_result = self.git.run_git_command(
                f"git merge {feature_name}", allow_failure=True
            )

            if merge_result["returncode"] != 0:
                if "Already up to date" in merge_result.get("stdout", ""):
                    self.colors.info("Ya está actualizado")
                else:
                    self.colors.error(f"Error al hacer merge de {feature_name}")
                    return
            else:
                self.colors.success("Merge completado")

            self.colors.info("\n⬆PASO 5: Subiendo cambios a develop...")
            push_result = self.git.run_git_command(
                "git push origin develop", allow_failure=True
            )

            if push_result["returncode"] != 0:
                if "Everything up-to-date" in push_result.get("stdout", ""):
                    self.colors.info("Todo está actualizado")
                else:
                    self.colors.error("Error al subir cambios a develop")
                    self.colors.info(" Intenta: git push origin develop")
                    return
            else:
                self.colors.success("Cambios subidos exitosamente a develop")

            self.colors.info("\n🧹 PASO 6: Limpieza opcional...")
            cleanup = input("¿Eliminar la rama feature local? (s/N): ").strip().lower()

            if cleanup in ["s", "si", "sí", "y", "yes"]:
                delete_local = self.git.run_git_command(
                    f"git branch -d {feature_name}", allow_failure=True
                )
                if delete_local["returncode"] == 0:
                    self.colors.success(f"Rama local {feature_name} eliminada")
                else:
                    self.git.run_git_command(
                        f"git branch -D {feature_name}", allow_failure=True
                    )

                remote_delete = (
                    input("¿Eliminar también del remoto? (s/N): ").strip().lower()
                )
                if remote_delete in ["s", "si", "sí", "y", "yes"]:
                    delete_remote = self.git.run_git_command(
                        f"git push origin --delete {feature_name}", allow_failure=True
                    )
                    if delete_remote["returncode"] == 0:
                        self.colors.success(f"Rama remota {feature_name} eliminada")

            self.colors.success("\n" + "=" * 60)
            self.colors.success("FLUJO GITFLOW COMPLETADO EXITOSAMENTE")
            self.colors.success("=" * 60)
            self.colors.info(f" Resumen de operaciones:")
            self.colors.info(
                f"   ✓ Rama feature: {Fore.YELLOW}{feature_name}{Fore.RESET}"
            )
            self.colors.info(f"   ✓ Mensaje commit: {Fore.CYAN}{message}{Fore.RESET}")
            self.colors.info(f"   ✓ Integrado en: {Fore.BLUE}develop{Fore.RESET}")
            self.colors.info(f"   ✓ Subido a: {Fore.GREEN}origin/develop{Fore.RESET}")

            self.colors.info("\n📊 Estado final:")
            self.git.run_git_command("git status")

            self.git_logger.log_operation(
                "FEATURE_BRANCH_WORKFLOW",
                f"GitFlow completado: {feature_name} → develop",
                "SUCCESS",
            )

        except Exception as e:
            self.colors.error(f"Error en el flujo: {str(e)}")
            self.git_logger.log_error(str(e), "feature_branch_workflow")
