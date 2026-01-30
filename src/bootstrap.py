from src.infrastructure.storage.fs_skill_store import FSSkillStore
from src.infrastructure.llm.openai_client import OpenAIClient
from src.infrastructure.runners.subprocess_runner import SubprocessRunner
from src.infrastructure.mcp.stdio_client import MCPStdioClient
from src.services.orchestrator import Orchestrator
from src.settings import settings


class AppContainer:
    """
    Contenedor de dependencias (Simple DI).
    Instancia las implementaciones concretas de infraestructura
    y las inyecta en los servicios de aplicación.
    """

    def __init__(self):
        # 1. Infrastructure Layer
        self.skill_store = FSSkillStore(skills_dir=settings.SKILLS_DIR)
        self.llm_client = OpenAIClient()
        self.runner = SubprocessRunner(workspace_dir=settings.WORKSPACE_DIR)

        # Configuración de MCP (Context7)
        self.mcp_client = MCPStdioClient(
            command="python3", args=["scripts/context7_mcp_bridge.py"]
        )

        # 2. Application Layer
        self.orchestrator = Orchestrator(
            skill_store=self.skill_store,
            llm_client=self.llm_client,
            runner=self.runner,
            mcp_client=self.mcp_client,
        )


def bootstrap() -> Orchestrator:
    """
    Punto de entrada para inicializar la aplicación.
    Retorna el orquestador listo para usar.
    """
    container = AppContainer()
    return container.orchestrator
