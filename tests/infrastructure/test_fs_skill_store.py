import pytest
import os
import shutil
from src.infrastructure.storage.fs_skill_store import FSSkillStore

@pytest.fixture
def temp_skills_dir(tmp_path):
    """Crea un directorio temporal con skills de prueba."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Skill 1: Web Research
    web_dir = skills_dir / "web-research"
    web_dir.mkdir()
    (web_dir / "SKILL.md").write_text("""---
name: web-research
description: Busca en la web.
version: 1.1.0
metadata:
  entry_script: scripts/search.py
---
Instrucciones completas aquí.
""")
    
    # Skill 2: Data Analysis
    data_dir = skills_dir / "data-analysis"
    data_dir.mkdir()
    (data_dir / "SKILL.md").write_text("""---
name: data-analysis
description: Analiza datos.
---
Instrucciones de análisis.
""")
    
    return str(skills_dir)

@pytest.mark.asyncio
async def test_get_all_metadata(temp_skills_dir):
    store = FSSkillStore(temp_skills_dir)
    metadata_list = await store.get_all_metadata()
    
    assert len(metadata_list) == 2
    names = [m.name for m in metadata_list]
    assert "web-research" in names
    assert "data-analysis" in names
    
    web_meta = next(m for m in metadata_list if m.name == "web-research")
    assert web_meta.description == "Busca en la web."
    assert web_meta.version == "1.1.0"

@pytest.mark.asyncio
async def test_get_skill_doc(temp_skills_dir):
    store = FSSkillStore(temp_skills_dir)
    doc = await store.get_skill_doc("web-research")
    
    assert doc is not None
    assert doc.metadata.name == "web-research"
    assert "Instrucciones completas aquí." in doc.instructions
    assert doc.entry_script == "scripts/search.py"

@pytest.mark.asyncio
async def test_get_non_existent_skill(temp_skills_dir):
    store = FSSkillStore(temp_skills_dir)
    doc = await store.get_skill_doc("ghost-skill")
    assert doc is None
