# 🧠 Diseño del Sistema de Skills (Habilidades)

Este documento detalla el funcionamiento interno de las habilidades del agente, siguiendo el patrón de **Progressive Disclosure** (Revelación Progresiva) para optimizar el uso del contexto del LLM.

---

## 🏗️ Estructura de una Skill

Cada habilidad reside en su propio directorio dentro de `workspace/skills/`. Este enfoque modular permite añadir o quitar capacidades sin tocar el código fuente del agente.

```text
workspace/skills/<skill-name>/
├── SKILL.md              # Contrato y guía (Niveles 1 y 2)
├── scripts/              # Brazo motor (Python/Bash)
│   └── main_script.py
└── references/           # Documentación profunda (Nivel 3)
```

---

## 🌊 Flujo de Revelación Progresiva

El sistema gestiona el contexto en tres niveles para evitar la saturación del LLM.

### Diagrama de Flujo de Contexto

```mermaid
graph TD
    A[Inicio de Sesión] --> B{Router LLM}
    B -- "Nivel 1: Metadata" --> C[Discovery]
    C -- "Usuario pregunta algo específico" --> D[Selección de Skill]
    D -- "Nivel 2: SKILL.md" --> E[Instrucciones Completas]
    E -- "Skill requiere datos técnicos" --> F[Carga de Referencias]
    F -- "Nivel 3: Resources" --> G[Conocimiento Profundo]
    G --> H[Ejecución de Acción]
```

### Detalle de los Niveles

| Nivel | Componente | Implementación Técnica | Propósito |
| :--- | :--- | :--- | :--- |
| **1** | **Metadata** | `FSSkillStore.get_all_metadata()` | Proporciona al Router el nombre y la descripción breve de todas las skills para que sepa qué puede hacer. |
| **2** | **Instrucciones** | `FSSkillStore.get_skill_doc()` | Carga el contenido de `SKILL.md` (sin frontmatter). Proporciona el "know-how" y el contrato de parámetros. |
| **3** | **Recursos** | Lectura directa de archivos en `references/` | Información técnica que solo se carga si el agente lo solicita explícitamente tras leer el Nivel 2. |

---

## ⚙️ Ciclo de Ejecución de una Skill

El proceso de ejecución está estrictamente separado del razonamiento para garantizar la seguridad y la estabilidad del sistema.

### Diagrama de Secuencia de Ejecución

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant R as SubprocessRunner
    participant S as Python Script
    participant LLM as Router LLM

    O->>LLM: Solicita decisión (con Metadata Nivel 1)
    LLM-->>O: Acción: skill="weather", args={"city": "Madrid"}
    O->>O: Carga SKILL.md (Nivel 2)
    O->>R: Lanza proceso: python3 scripts/weather.py '{"city": "Madrid"}'
    R->>S: stdin (JSON args)
    S-->>R: stdout (JSON result)
    R-->>O: Observation Object
    O->>LLM: Inyecta Observation en el Historial
    LLM-->>O: Genera respuesta final al usuario
```

---

## 🛠️ Contrato de Datos (Input/Output)

Para mantener la independencia de tecnologías, las skills operan mediante **JSON estándar**:

1.  **Input**: El script recibe los argumentos como una cadena JSON en el primer argumento de línea de comandos (`sys.argv[1]`).
2.  **Output**: El script debe imprimir en `stdout` un objeto JSON válido.
3.  **Aislamiento**: Cada ejecución tiene un tiempo límite (`SKILL_TIMEOUT`) definido en las políticas de dominio.
