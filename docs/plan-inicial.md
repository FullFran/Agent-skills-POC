# 📄 INFORME TÉCNICO — POC AGENTE IA (SKILLS + MCP)

## Autor

POC técnica individual
Arquitectura Clean / Hexagonal
Objetivo: **entender y validar el modelo agentic tipo Clawbot/OpenCode**

---

## 1. Objetivo de la POC

Construir un **agente de línea de comandos** que:

1. Usa un **LLM como router de decisiones** (no como executor).
2. Descubre **skills declarativas desde filesystem**.
3. Integra **tools externas vía MCP (stdio)**.
4. Permite **skill chaining** controlado.
5. Devuelve **texto libre al usuario**, pero opera internamente con **contratos estructurados**.
6. Está diseñado para **escalar sin reescritura** (DB, workers, multi-tenant).

👉 Esta POC **no busca producto**, busca **comprensión profunda y arquitectura correcta**.

---

## 2. Alcance (qué entra y qué NO)

### Entra en esta POC

* Router basado en LLM con salida JSON estricta
* Loop agentic con múltiples pasos
* Skills locales (filesystem)
* Tools MCP vía stdio
* CLI interactiva
* Políticas básicas de seguridad y control

### NO entra

* UI
* Memoria larga persistente
* Multi-agent
* DB
* Workers remotos
* Seguridad avanzada
* Evaluación automática

Todo eso queda **explícitamente fuera**.

---

## 3. Principios arquitectónicos (innegociables)

1. **Decidir ≠ Ejecutar**
2. **Skill ≠ Tool**
3. **Workspace ≠ Runtime**
4. **Contratos antes que implementación**
5. **Escalabilidad por sustitución, no por extensión**

Si alguno de estos se rompe, el agente se degrada a “script con LLM”.

---

## 4. Arquitectura general

### 4.1 Flujo principal

```
Usuario
  ↓
CLI
  ↓
Agent Orchestrator
  ↓
Router (LLM → JSON)
  ↓
┌───────────────┬───────────────┐
│ Skill Runner  │ MCP Tool Call │
└───────────────┴───────────────┘
  ↓
Resultado normalizado
  ↓
¿stop? → sí → output usuario
        → no → nuevo ciclo
```

---

## 5. Estructura del repositorio (definitiva para POC)

```txt
my-agent/
├── .workspace/
│   ├── skills/
│   │   └── web-research/
│   │       ├── SKILL.md
│   │       └── scripts/search.py
│   ├── soul.md
│   └── tools.md
│
├── agent/
│   ├── domain/
│   │   ├── models.py
│   │   ├── ports.py
│   │   └── policies.py
│   │
│   ├── application/
│   │   ├── orchestrator.py
│   │   └── router_llm.py
│   │
│   ├── infrastructure/
│   │   ├── stores/fs_skill_store.py
│   │   ├── runners/script_runner.py
│   │   └── mcp/stdio_client.py
│   │
│   └── cli.py
│
└── README.md
```

---

## 6. Workspace (.workspace)

### 6.1 Skills (filesystem-first)

Cada skill es **una capacidad declarativa**, no “código suelto”.

```
skills/<skill-name>/
├── SKILL.md
└── scripts/
    └── <entry>.py
```

#### SKILL.md (contrato mínimo)

```md
---
name: web-research
description: Busca información reciente y devuelve un resumen con fuentes.
metadata:
  entry_script: scripts/search.py
inputs:
  q: string
outputs:
  summary: string
  sources: array
side_effects: network
---
```

📌 **Importante**:
El agente **nunca** asume cómo funciona la skill. Solo conoce este contrato.

---

### 6.2 Contexto base del agente

Solo dos archivos (el resto es overkill en POC):

* `soul.md` → tono, límites, comportamiento general
* `tools.md` → cómo y cuándo usar herramientas

Estos se inyectan **siempre** al router LLM.

---

## 7. Dominio (core del sistema)

### 7.1 Modelos clave (`domain/models.py`)

Conceptos que NO dependen de infraestructura:

* `SkillDoc`
* `Action`
* `ToolCall`
* `ExecutionResult`
* `AgentState`

Ejemplo conceptual de `Action`:

```json
{
  "type": "respond | skill | tool",
  "name": "web-research",
  "args": {},
  "reason": "por qué se eligió",
  "stop": false
}
```

---

### 7.2 Puertos (`domain/ports.py`)

Interfaces puras:

* `SkillStore`
* `ToolRegistry`
* `Runner`
* `LLMClient`

El orquestador **solo depende de esto**.

---

### 7.3 Políticas (`domain/policies.py`)

Valores explícitos, no mágicos:

* `MAX_STEPS = 6`
* `MAX_TOOL_CALLS = 10`
* `SKILL_TIMEOUT = 30s`
* `MCP_TIMEOUT = 60s`
* Allowlist de tools

Esto evita loops infinitos y comportamientos zombies.

---

## 8. Router LLM (pieza crítica)

### Responsabilidad

Convertir **estado + contexto** en una **acción estructurada válida**.

### Reglas duras

* Output **SIEMPRE JSON**
* Validación estricta (Pydantic o similar)
* Reintento con prompt de reparación
* Fallback seguro si falla

Ejemplo de output esperado:

```json
{
  "type": "skill",
  "name": "web-research",
  "args": { "q": "últimas noticias de IA" },
  "reason": "necesito información actualizada",
  "stop": false
}
```

📌 El router **no ejecuta nada**.
Si ejecuta, rompiste Clean.

---

## 9. Orchestrator (loop agentic)

### Algoritmo simplificado

1. Inicializar estado
2. Mientras `steps < MAX_STEPS`:

   * pedir acción al router
   * ejecutar acción (skill o tool)
   * normalizar resultado
   * agregar observación al contexto
   * si `stop == true` → salir
3. Devolver output final al usuario

### Clave

* Una skill **puede provocar otra decisión**
* No hay “plan maestro”, hay **razonamiento iterativo**

---

## 10. Ejecución

### 10.1 Skills locales

* Ejecutadas vía `ScriptRunner`
* Input: JSON por stdin
* Output: JSON por stdout
* Manejo explícito de errores

Primero **sin subprocess complejo**.
Aislamiento fuerte puede venir después.

---

### 10.2 Tools MCP (stdio)

Alcance de la POC:

* stdio únicamente
* JSON-RPC 2.0
* 1 cliente por servidor

Flujo:

1. spawn proceso
2. initialize
3. tools/list
4. tools/call

El agente ve las tools MCP como **acciones disponibles**, no como magia.

---

## 11. CLI (para demo real)

Comandos mínimos:

```bash
agent list-skills
agent list-tools
agent chat "pregunta del usuario"
```

En modo verbose:

* acción decidida
* resultado por step
* estado final

Esto es lo que hace creíble la POC frente al equipo.

---

## 12. Seguridad mínima (consciente)

En esta fase:

* Allowlist explícita de tools
* No auto-confirmar acciones destructivas
* Timeouts estrictos
* Sin HTTP MCP

No más. No menos.

---

## 13. Pruebas mínimas obligatorias

4 tests que justifican el diseño:

1. Skill discovery desde FS
2. Validación de schema del router
3. Corte por `MAX_STEPS`
4. Contrato de ejecución (JSON válido / error controlado)

Si esto pasa, el sistema **no es humo**.

---

## 14. Resultado esperado de la POC

Al finalizar:

* Entendés **qué es una skill de verdad**
* Entendés **qué rol cumple MCP**
* Tenés un agente que:

  * decide
  * ejecuta
  * se equivoca sin romperse
* La arquitectura está lista para:

  * DB
  * workers
  * multi-tenant
  * producto real

Sin reescribir el core.

