# Mejores Prácticas: Anthropic Agent Skills

Resumen de las directrices de Anthropic para la creación de habilidades de agentes (Skills).

## Principios Fundamentales

### 1. La Concisión es Clave
- El contexto es un recurso limitado. Cada token debe justificarse.
- **Suposición por defecto**: El modelo ya es inteligente. No expliques conceptos básicos (ej. qué es un PDF). Solo proporciona el contexto que el modelo NO tiene.
- Mantener `SKILL.md` por debajo de las **500 líneas**. Si crece más, usar Progressive Disclosure (vínculos a otros archivos).

### 2. Grados de Libertad Apropiados
- **Alta libertad**: Para tareas heurísticas (ej. revisión de código). Instrucciones basadas en texto.
- **Media libertad**: Patrones preferidos pero con flexibilidad (ej. pseudocódigo con parámetros).
- **Baja libertad**: Para tareas frágiles o críticas (ej. migraciones de DB). Scripts específicos sin parámetros.

### 3. Naming y Descripciones
- **Naming**: Usar forma de gerundio (`processing-pdfs`, `analyzing-data`).
- **Descripciones**: Escribir siempre en **tercera persona**. Incluir qué hace la skill y CUÁNDO usarla (triggers).

## Patrones de Progressive Disclosure

- **Referencias a un nivel**: Evitar anidamiento profundo de archivos. `SKILL.md` -> `reference.md` (Bien). `SKILL.md` -> `advanced.md` -> `details.md` (Mal).
- **Tabla de Contenidos**: Para archivos de referencia largos (>100 líneas), incluir un TOC al principio para que el modelo vea el scope incluso con lecturas parciales.

## Workflows y Feedback Loops

- **Checklists**: Proporcionar checklists que el agente pueda copiar y marcar en su respuesta para tareas complejas.
- **Validación Inmediata**: Patrón "Ejecutar validador -> Corregir errores -> Repetir".
- **Salidas Intermedias Verificables**: En tareas batch, crear primero un plan (ej. `plan.json`), validarlo con un script, y luego ejecutar.

## Desarrollo Iterativo

1. **Identificar gaps**: Ejecutar tareas sin la skill para ver dónde falla el modelo.
2. **Crear evaluaciones**: Definir casos de prueba antes de escribir la documentación.
3. **Instrucciones mínimas**: Escribir lo justo para pasar las evaluaciones.
4. **Refinar con el propio modelo**: Usar una instancia del modelo para ayudar a redactar las instrucciones de la skill.
