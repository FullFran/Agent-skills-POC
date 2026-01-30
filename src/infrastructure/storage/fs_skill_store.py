import yaml
import os
from typing import List, Optional
from src.core.interfaces.ports import ISkillStore
from src.core.schemas.models import SkillMetadata, SkillDoc

class FSSkillStore(ISkillStore):
    """
    Implementación de infraestructura para cargar skills desde el Filesystem.
    Sigue el patrón de Progressive Disclosure.
    """
    
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir

    async def get_all_metadata(self) -> List[SkillMetadata]:
        """Nivel 1: Escanea directorios y extrae frontmatter."""
        skills_metadata = []
        if not os.path.exists(self.skills_dir):
            return []
            
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            skill_file = os.path.join(skill_path, "SKILL.md")
            
            if os.path.isdir(skill_path) and os.path.exists(skill_file):
                metadata = self._extract_metadata(skill_file)
                if metadata:
                    skills_metadata.append(metadata)
        
        return skills_metadata

    async def get_skill_doc(self, name: str) -> Optional[SkillDoc]:
        """Nivel 2: Carga el documento completo para una skill específica."""
        skill_file = os.path.join(self.skills_dir, name, "SKILL.md")
        if not os.path.exists(skill_file):
            return None
            
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("---")
        if len(parts) < 3:
            return None
            
        frontmatter = yaml.safe_load(parts[1])
        instructions = parts[2].strip()
        
        metadata = SkillMetadata(
            name=frontmatter.get("name", name),
            description=frontmatter.get("description", ""),
            version=frontmatter.get("version", "1.0.0")
        )
        
        return SkillDoc(
            metadata=metadata,
            instructions=instructions,
            entry_script=frontmatter.get("metadata", {}).get("entry_script"),
            references=frontmatter.get("references", [])
        )

    def _extract_metadata(self, file_path: str) -> Optional[SkillMetadata]:
        """Auxiliar para leer solo el frontmatter (Nivel 1)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            parts = content.split("---")
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                return SkillMetadata(
                    name=frontmatter.get("name", "unknown"),
                    description=frontmatter.get("description", ""),
                    version=frontmatter.get("version", "1.0.0")
                )
        except Exception:
            return None
        return None
