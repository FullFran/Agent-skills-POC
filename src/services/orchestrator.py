from typing import List, Dict, Any, Optional
from src.core.interfaces.ports import ISkillStore, ILLMClient, IRunner, IMCPClient
from src.core.schemas.models import AgentState, Action, Observation, ActionType
import logging

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Agent Orchestrator (Application Layer).
    Implementa el loop agentic in-memory.
    """

    def __init__(
        self,
        skill_store: ISkillStore,
        llm_client: ILLMClient,
        runner: IRunner,
        mcp_client: Optional[IMCPClient] = None,
    ):
        self.skill_store = skill_store
        self.llm = llm_client
        self.runner = runner
        self.mcp = mcp_client
        self.max_steps = 6  # Definido en policies.py (Plan Inicial)

    async def chat(self, user_prompt: str, on_step_cb=None) -> str:
        """Punto de entrada para la CLI."""

        # 1. Inicialización de sesión volátil
        state = AgentState(session_id="session_poc")
        state.add_message("user", user_prompt)

        # Cargar catálogo Nivel 1 (Metadata) para el Router
        state.available_skills = await self.skill_store.get_all_metadata()

        # 2. Loop Agentic
        while state.steps < self.max_steps and not state.is_complete:
            # A. Fase de Decisión (Router LLM)
            action: Action = await self.llm.ask(state)

            if on_step_cb:
                await on_step_cb(state.steps, action)

            if action.type == "respond" or action.stop:
                state.is_complete = True
                return action.args.get("response", "No pude generar una respuesta.")

            # D. Registrar la acción en el historial (para que el LLM sepa qué decidió)
            state.add_message(
                "assistant",
                f"Decision: {action.type}:{action.name} ({action.reason}) Args: {action.args}",
            )

            # B. Fase de Ejecución
            observation: Optional[Observation] = None

            if action.type == "skill":
                # Nivel 2: Si el agente elige una skill, cargamos su doc completo antes de ejecutar
                # (Nota: En esta POC, la ejecución incluye la carga del contrato de la skill)
                skill_doc = await self.skill_store.get_skill_doc(action.name)
                if skill_doc:
                    observation = await self.runner.run(skill_doc, action.args)
                else:
                    observation = Observation(
                        origin=action.name,
                        content=f"Error: Skill '{action.name}' no encontrada.",
                        status="error",
                    )

            elif action.type == "tool" and self.mcp:
                # Ejecución vía MCP
                observation = await self.mcp.call_tool(action.name, action.args)

            # C. Fase de Observación
            if observation:
                state.add_observation(observation)
            else:
                state.add_message(
                    "system", "Error: La acción no produjo ninguna observación."
                )
                state.steps += 1

        return "Se alcanzó el límite de pasos permitido para esta tarea."
