from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata Nivel 1: Descubrimiento rápido."""

    name: str
    description: str
    version: Optional[str] = "1.0.0"


class SkillDoc(BaseModel):
    """Metadata Nivel 2: Instrucciones completas (Progressive Disclosure)."""

    metadata: SkillMetadata
    instructions: str  # Contenido del SKILL.md (sin frontmatter)
    entry_script: Optional[str] = None
    references: List[str] = Field(
        default_factory=list
    )  # Nivel 3: Links a otros archivos


from enum import Enum


class ActionType(str, Enum):
    """Tipos de acciones soportadas según el Plan Inicial."""

    SKILL = "skill"
    TOOL = "tool"
    RESPOND = "respond"


class Action(BaseModel):
    """Decisión estructurada del Router LLM."""

    type: str  # skill | tool | respond
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    reason: str  # El "por qué" de la decisión (Chain of Thought)
    stop: bool = False


class Observation(BaseModel):
    """Resultado normalizado de una ejecución."""

    origin: str  # Nombre de la skill o tool ejecutada
    content: Any
    status: str = "success"  # success | error
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Estado volátil de la sesión (In-Memory)."""

    session_id: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    steps: int = 0
    observations: List[Observation] = Field(default_factory=list)
    # Catálogo cargado en Nivel 1 para el Router
    available_skills: List[SkillMetadata] = Field(default_factory=list)
    is_complete: bool = False

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def add_observation(self, observation: Observation):
        self.observations.append(observation)
        # Inyectamos el resultado en el historial.
        # Usamos role 'user' con un prefijo claro porque algunos modelos
        # ignoran mensajes 'system' en mitad de la conversación.
        prefix = "SUCCESS" if observation.status == "success" else "ERROR"
        msg = f"[SYSTEM OBSERVATION] Result from {observation.origin} ({prefix}):\n{observation.content}"
        self.add_message("user", msg)
        self.steps += 1
