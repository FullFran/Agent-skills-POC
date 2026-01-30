import os
import json
from openai import AsyncOpenAI
from src.core.interfaces.ports import ILLMClient
from src.core.schemas.models import AgentState, Action, SkillMetadata
from src.settings import settings


class OpenAIClient(ILLMClient):
    """
    Cliente LLM que utiliza la API de OpenAI (o compatibles).
    Actúa como el 'Router' que decide la siguiente acción.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL
        )
        self.model = settings.LLM_MODEL

    async def ask(self, state: AgentState) -> Action:
        # 1. Cargar contexto del Workspace (Soul + Skills Metadata)
        soul_content = self._load_workspace_file("soul.md")
        tools_content = self._load_workspace_file("tools.md")

        # 2. Construir el System Prompt
        system_prompt = self._build_system_prompt(
            soul_content, tools_content, state.available_skills
        )

        # 3. Llamada al LLM con salida JSON estricta
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, *state.history],
                response_format={"type": "json_object"},
                temperature=0,  # Necesitamos precisión para el routing
            )

            raw_content = response.choices[0].message.content
            action_data = json.loads(raw_content)

            # Validación vía Pydantic (si falla, levanta ValidationError)
            return Action(**action_data)

        except Exception as e:
            # Fallback seguro: responder al usuario con el error
            return Action(
                type="respond",
                name="error_handler",
                args={"response": f"Error en el Router LLM: {str(e)}"},
                reason="Falla técnica en la comunicación con el LLM.",
                stop=True,
            )

    def _load_workspace_file(self, filename: str) -> str:
        path = os.path.join(settings.WORKSPACE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _build_system_prompt(
        self, soul: str, tools: str, skills: list[SkillMetadata]
    ) -> str:
        skills_summary = "\n".join([f"- {s.name}: {s.description}" for s in skills])

        return f"""
{soul}

## Herramientas Externas (MCP)
{tools}

## Habilidades Disponibles (Agent Skills - Nivel 1)
{skills_summary}

## Instrucciones de Respuesta - FORMATO JSON ESTRICTO
Debes responder SIEMPRE con un objeto JSON que siga esta estructura exacta:
{{
  "type": "skill" | "tool" | "respond",
  "name": "nombre_de_la_skill_o_tool",
  "args": {{
    "parametro_1": "valor"
  }},
  "reason": "explicación de tu razonamiento",
  "stop": false
}}

### Reglas Críticas:
1. NO respondas con texto plano, solo JSON.
2. NO omitas los campos "type", "name", "args" o "reason". Son OBLIGATORIOS.
3. Si quieres responder al usuario, usa "type": "respond", "name": "final_answer" y pon tu respuesta en "args": {{"response": "..."}}.
4. Si una skill no devuelve la información tras 1 o 2 intentos, admítelo y responde al usuario.

### Ejemplo:
{{
  "type": "skill",
  "name": "real-search",
  "args": {{ "query": "fifi mechanical keyboard" }},
  "reason": "El usuario pregunta por un producto específico que requiere búsqueda externa.",
  "stop": false
}}
"""
