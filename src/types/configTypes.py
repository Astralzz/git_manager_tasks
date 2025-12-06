# Tipos

from typing import TypedDict, Optional, Callable, Protocol, Literal, List, Dict


# Protocolo para el logger
class LoggerProtocol(Protocol):
    def log_user_input(self, input_type: str, value: str) -> None: ...
    def log_warning(self, warning_message: str, context: str = "") -> None: ...
    def log_success(self, success_message: str, context: str = "") -> None: ...
    def log_error(self, error_message: str, context: str = "") -> None: ...
    def log_program_end(self) -> None: ...
    def log_menu_selection(self, option_number: int, option_description: str) -> None: ...
    def log_operation(self, operation: str, details: str = "", status: "LogStatus" = "INFO") -> None: ...
    def log_git_command(self, command: str, result: "GitCommandResult") -> None: ...
    def log_branch_operation(self, operation: str, branch_name: str, details: str = "") -> None: ...
    def log_rebase_operation(self, base_branch: str, feature_branch: str, status: "LogStatus" = "INFO") -> None: ...
    def log_pull_operation(self, branch_name: str, status: "LogStatus" = "INFO") -> None: ...
    def log_push_operation(self, branch_name: str, commit_message: str, status: "LogStatus" = "INFO") -> None: ...
    def log_stash_operation(self, operation: str, stash_message: str = "", status: "LogStatus" = "INFO") -> None: ...
    def log_program_start(self, config: "ExtendedConfigType") -> None: ...
    def read_today_log(self) -> str: ...
    def get_today_log_path(self) -> str: ...


# Tipo para las configuraciones base
class ConfigType(TypedDict):
    number: int
    id: str
    name: str
    email: str
    username: str
    token: str
    branch: str


# Tipo para las configuraciones con ruta completa del repositorio
class ConfigWithPathType(ConfigType):
    repo_path: str


# Tipo para configuraciones extendidas con campos opcionales
class ExtendedConfigType(ConfigWithPathType, total=False):
    base_branch: str
    feature_branch: Optional[str]
    project: Optional[str]
    section: Optional[str]
    task: Optional[str]
    date: Optional[str]


# Tipo para secciones de configuración
class ConfigSection(TypedDict):
    description: str
    configs: List[Dict]


# Tipo para configuraciones opcionales durante la carga
class PartialConfigType(TypedDict, total=False):
    number: Optional[int]
    id: Optional[str]
    name: Optional[str]
    email: Optional[str]
    username: Optional[str]
    token: Optional[str]
    repo: Optional[str]
    branch: Optional[str]
    repo_path: Optional[str]
    base_branch: str
    feature_branch: Optional[str]
    project: Optional[str]
    section: Optional[str]
    task: Optional[str]


# Tipo para las opciones del menú
class MenuOptionType(TypedDict):
    function: Callable[[], None]
    description: str


# Tipo para el resultado de comandos Git
class GitCommandResult(TypedDict):
    returncode: int
    stdout: str
    stderr: str


# Tipos literales para los status de log
LogStatus = Literal["INFO", "SUCCESS", "WARNING", "ERROR"]
