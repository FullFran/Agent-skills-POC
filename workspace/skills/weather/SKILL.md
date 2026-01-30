---
name: weather
description: Obtiene el clima actual de cualquier ciudad del mundo.
version: 1.0.0
metadata:
  entry_script: scripts/weather.py
inputs:
  city: string (Nombre de la ciudad, ej: 'Madrid', 'Buenos Aires')
outputs:
  summary: string (Resumen del clima actual)
  temperature: number (Temperatura en Celsius)
---

# Weather Skill

Proporciona información meteorológica en tiempo real usando la API de Open-Meteo.

## Instrucciones
1. Recibe el nombre de una ciudad.
2. Traduce la ciudad a coordenadas (Geocoding interno o vía API).
3. Devuelve la temperatura y el estado del cielo.
