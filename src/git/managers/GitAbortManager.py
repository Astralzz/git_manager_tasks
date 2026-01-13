from typing import List
from src.types.configTypes import MenuOptionType


class GitAbortManager:
    """Clase para manejar operaciones de abort en Git (cancelar operaciones en progreso)"""

    def __init__(self, git_instance):
        """Inicializa el gestor de abort con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger

    def abort_menu(self) -> None:
        """Muestra el menú de operaciones de abort"""
        self.colors.info("\n🟥 MENÚ DE CANCELACIÓN DE OPERACIONES")
        self.colors.info("=" * 60)
        
        options: List["MenuOptionType"] = [
            {
                "function": self.abort_merge,
                "description": "🔴 Cancelar merge en progreso",
            },
            {
                "function": self.abort_rebase,
                "description": "🔴 Cancelar rebase en progreso",
            },
            {
                "function": self.abort_cherry_pick,
                "description": "🔴 Cancelar cherry-pick en progreso",
            },
        ]
        
        self.git.show_menu(options, is_submenu=True)

    def abort_merge(self) -> None:
        """Cancela un merge en progreso"""
        self.git.ask_pass()

        abort_result = self.git.run_git_command("git merge --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("✅ Merge cancelado exitosamente.")
            self.git_logger.log_operation(
                "MERGE_ABORT", "Merge cancelado", "SUCCESS"
            )
        else:
            self.colors.warning("⚠️ No hay merge en progreso para cancelar.")
            self.git_logger.log_operation(
                "MERGE_ABORT", "No hay merge en progreso", "WARNING"
            )

    def abort_rebase(self) -> None:
        """Cancela un rebase en progreso"""
        self.git.ask_pass()

        abort_result = self.git.run_git_command("git rebase --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("✅ Rebase cancelado exitosamente.")
            self.git_logger.log_operation(
                "REBASE_ABORT", "Rebase cancelado", "SUCCESS"
            )
        else:
            self.colors.warning("⚠️ No hay rebase en progreso para cancelar.")
            self.git_logger.log_operation(
                "REBASE_ABORT", "No hay rebase en progreso", "WARNING"
            )

    def abort_cherry_pick(self) -> None:
        """Cancela un cherry-pick en progreso"""
        self.git.ask_pass()

        abort_result = self.git.run_git_command("git cherry-pick --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("✅ Cherry-pick cancelado exitosamente.")
            self.git_logger.log_operation(
                "CHERRY_PICK_ABORT", "Cherry-pick cancelado", "SUCCESS"
            )
        else:
            self.colors.warning("⚠️ No hay cherry-pick en progreso para cancelar.")
            self.git_logger.log_operation(
                "CHERRY_PICK_ABORT", "No hay cherry-pick en progreso", "WARNING"
            )
