import subprocess
import json
import os
from src.core.interfaces.ports import IRunner
from src.core.schemas.models import SkillDoc, Observation

class SubprocessRunner(IRunner):
    """
    Ejecutor de scripts locales mediante subprocess.
    Sigue el contrato de la POC: Input/Output vía JSON.
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    async def run(self, skill: SkillDoc, args: dict) -> Observation:
        if not skill.entry_script:
            return Observation(
                origin=skill.metadata.name,
                content="Error: La skill no tiene definido un entry_script.",
                status="error"
            )
            
        script_path = os.path.join(self.workspace_dir, "skills", skill.metadata.name, skill.entry_script)
        
        if not os.path.exists(script_path):
            return Observation(
                origin=skill.metadata.name,
                content=f"Error: Script no encontrado en {script_path}",
                status="error"
            )

        try:
            # Ejecutamos el script pasando los argumentos como JSON string
            process = subprocess.run(
                ["python3", script_path, json.dumps(args)],
                capture_output=True,
                text=True,
                timeout=30 # Política SKILL_TIMEOUT
            )
            
            if process.returncode != 0:
                return Observation(
                    origin=skill.metadata.name,
                    content=f"Error en ejecución: {process.stderr}",
                    status="error"
                )
            
            # Intentamos parsear la salida como JSON
            try:
                output_data = json.loads(process.stdout)
            except json.JSONDecodeError:
                output_data = process.stdout.strip()
                
            return Observation(
                origin=skill.metadata.name,
                content=output_data,
                status="success"
            )
            
        except subprocess.TimeoutExpired:
            return Observation(
                origin=skill.metadata.name,
                content="Error: Tiempo de ejecución excedido (Timeout).",
                status="error"
            )
        except Exception as e:
            return Observation(
                origin=skill.metadata.name,
                content=f"Error inesperado: {str(e)}",
                status="error"
            )
