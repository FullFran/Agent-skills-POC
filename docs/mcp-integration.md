# 🔌 Integración MCP (Model Context Protocol)

Este documento explica cómo el agente utiliza el protocolo **MCP** para extender sus capacidades mediante herramientas externas alojadas en servidores independientes.

---

## 🧐 ¿Por qué MCP?

Mientras que las **Skills** son capacidades locales acopladas al filesystem del agente, el protocolo **MCP** permite:
- Conectar servicios de terceros (Context7, GitHub, Slack).
- Reutilizar herramientas existentes sin reescribir código.
- Escalar la arquitectura de forma distribuida.

---

## 🏗️ Arquitectura del Cliente MCP

Nuestra implementación utiliza el transporte **stdio** (entrada/salida estándar) para comunicarse con los servidores MCP mediante mensajes **JSON-RPC 2.0**.

### Diagrama de Comunicación

```mermaid
graph LR
    subgraph Core_Agent[Agente Core]
        Orch[Orchestrator]
        Client[MCP Stdio Client]
    end

    subgraph External_Server[Servidor MCP]
        Bridge[MCP Bridge / Server]
        Tools[Tools Registry]
    end

    Orch -- "Llamada a Tool" --> Client
    Client -- "JSON-RPC (stdin)" --> Bridge
    Bridge -- "Ejecutar Lógica" --> Tools
    Tools -- "Resultado JSON" --> Bridge
    Bridge -- "JSON-RPC (stdout)" --> Client
    Client -- "Observation" --> Orch
```

---

## 🛠️ Herramientas de Context7 (Ejemplo)

Actualmente, el sistema integra un puente para las herramientas de **Context7**, permitiendo al agente consultar documentación técnica de librerías.

### Flujo de Resolución de Documentación

```mermaid
sequenceDiagram
    participant A as Agente
    participant M as MCP Client
    participant C as Context7 Bridge

    A->>M: call_tool("resolve-library-id", {"libraryName": "pydantic"})
    M->>C: {"method": "tools/call", "params": {"name": "resolve-library-id", ...}}
    C-->>M: {"result": {"libraryId": "/pydantic/pydantic"}}
    M-->>A: Observation (Success)
    
    A->>M: call_tool("query-docs", {"libraryId": "/pydantic/pydantic", "query": "BaseModel"})
    M->>C: {"method": "tools/call", "params": {"name": "query-docs", ...}}
    C-->>M: {"result": {"content": "Documentación técnica..."}}
    M-->>A: Observation (Success)
```

---

## ⚙️ Configuración y Extensibilidad

Para añadir un nuevo servidor MCP, solo es necesario:
1.  Definir el comando de arranque en el `AppContainer` (`src/bootstrap.py`).
2.  Actualizar el archivo `workspace/tools.md` para que el agente conozca las nuevas herramientas disponibles.
3.  El orquestador gestionará automáticamente el ciclo de vida del proceso hijo (spawn/terminate).
