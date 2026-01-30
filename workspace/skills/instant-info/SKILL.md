---
name: instant-info
description: Obtiene información real y resúmenes instantáneos de internet sobre conceptos, personas o tecnologías.
version: 1.0.0
metadata:
  entry_script: scripts/lookup.py
inputs:
  query: string (el término o concepto a buscar)
outputs:
  summary: string (la definición o información encontrada)
  source: string (fuente de la información)
---

# Instant Info Skill

Proporciona datos veraces y resúmenes directos desde la API de DuckDuckGo.

## Cuándo usar
- Para obtener definiciones rápidas de términos técnicos.
- Para conocer quién es una persona famosa o qué es una tecnología.
- Cuando necesitas un dato "enciclopédico" actualizado.
