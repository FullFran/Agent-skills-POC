# Estudio de Referencia: custom-agent-with-skills

Este documento resume los aprendizajes extraídos del repositorio [custom-agent-with-skills](https://github.com/coleam00/custom-agent-with-skills).

## Concepto Core: Progressive Disclosure

La idea central es gestionar el contexto del LLM de forma eficiente mediante tres niveles de carga de información:

### Nivel 1: Metadata (Descubrimiento)
- **Token cost**: ~100 tokens por skill.
- **Ubicación**: Se inyecta en el system prompt.
- **Contenido**: Nombre y descripción breve (1-2 frases).
- **Propósito**: El agente decide qué skill es relevante para la tarea sin cargar todos los detalles.

### Nivel 2: Instrucciones Completas (Carga bajo demanda)
- **Token cost**: Variable, solo cuando se activa.
- **Ubicación**: Archivo `SKILL.md` en el directorio de la skill.
- **Contenido**: Detalles técnicos, guías paso a paso, ejemplos de uso.
- **Propósito**: Proporcionar al agente el "know-how" específico una vez que ha decidido usar la capacidad.

### Nivel 3: Recursos y Referencias (Carga granular)
- **Token cost**: Mínimo, solo partes específicas.
- **Ubicación**: Directorios `references/` o `scripts/` dentro de la skill.
- **Contenido**: Documentación de APIs, checklists de seguridad, scripts de validación.
- **Propósito**: Información de apoyo profunda que el agente consulta solo si las instrucciones del Nivel 2 lo requieren.

## Implementación Técnica Observada

1. **SkillLoader**: Clase encargada de escanear el filesystem, validar los frontmatter de los `SKILL.md` y generar el catálogo para el LLM.
2. **Framework Agnostic**: Aunque el repo de ejemplo usa Pydantic AI, el patrón es aplicable a cualquier arquitectura (incluyendo la nuestra de "cero frameworks").
3. **Validación**: Uso de scripts para asegurar que las skills cumplen con el contrato definido antes de ser publicadas.

## Aplicación en nuestro proyecto

Adoptaremos este modelo de **Progressive Disclosure** para nuestro Workspace, asegurando que el router LLM no se sature con instrucciones innecesarias de capacidades que no va a utilizar en el turno actual.
