from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.schemas.models import SkillMetadata, SkillDoc, Action, Observation, AgentState

class ISkillStore(ABC):
    """Puerto para el descubrimiento y carga de skills (Filesystem)."""
    
    @abstractmethod
    async def get_all_metadata(self) -> List[SkillMetadata]:
        """Nivel 1: Lista todas las skills disponibles."""
        pass

    @abstractmethod
    async def get_skill_doc(self, name: str) -> Optional[SkillDoc]:
        """Nivel 2: Carga instrucciones completas de una skill."""
        pass

class ILLMClient(ABC):
    """Puerto para la comunicación con el LLM (Router)."""
    
    @abstractmethod
    async def ask(self, state: AgentState) -> Action:
        """Convierte estado + contexto en una Acción estructurada."""
        pass

class IRunner(ABC):
    """Puerto para la ejecución de scripts locales."""
    
    @abstractmethod
    async def run(self, skill: SkillDoc, args: dict) -> Observation:
        """Ejecuta el entry_script de una skill."""
        pass

class IMCPClient(ABC):
    """Puerto para herramientas externas vía MCP (stdio)."""
    
    @abstractmethod
    async def call_tool(self, tool_name: str, args: dict) -> Observation:
        """Llama a una tool de un servidor MCP."""
        pass
