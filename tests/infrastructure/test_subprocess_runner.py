import pytest
import os
import json
from src.infrastructure.runners.subprocess_runner import SubprocessRunner
from src.core.schemas.models import SkillDoc, SkillMetadata

@pytest.fixture
def temp_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    skills_dir = workspace / "skills" / "test-skill" / "scripts"
    skills_dir.mkdir(parents=True)
    
    # Creamos un script de prueba exitoso
    success_script = skills_dir / "success.py"
    success_script.write_text("""
import sys
import json
args = json.loads(sys.argv[1])
print(json.dumps({"received": args, "status": "ok"}))
""")
    
    # Creamos un script que falla
    fail_script = skills_dir / "fail.py"
    fail_script.write_text("""
import sys
sys.stderr.write("Algo salio mal")
sys.exit(1)
""")

    return str(workspace)

@pytest.mark.asyncio
async def test_run_success(temp_workspace):
    runner = SubprocessRunner(temp_workspace)
    skill = SkillDoc(
        metadata=SkillMetadata(name="test-skill", description="test"),
        instructions="...",
        entry_script="scripts/success.py"
    )
    
    args = {"input": "hola"}
    observation = await runner.run(skill, args)
    
    assert observation.status == "success"
    assert observation.content["received"] == args
    assert observation.content["status"] == "ok"

@pytest.mark.asyncio
async def test_run_fail(temp_workspace):
    runner = SubprocessRunner(temp_workspace)
    skill = SkillDoc(
        metadata=SkillMetadata(name="test-skill", description="test"),
        instructions="...",
        entry_script="scripts/fail.py"
    )
    
    observation = await runner.run(skill, {})
    assert observation.status == "error"
    assert "Algo salio mal" in observation.content

@pytest.mark.asyncio
async def test_run_no_script(temp_workspace):
    runner = SubprocessRunner(temp_workspace)
    skill = SkillDoc(
        metadata=SkillMetadata(name="test-skill", description="test"),
        instructions="..."
    )
    
    observation = await runner.run(skill, {})
    assert observation.status == "error"
    assert "no tiene definido un entry_script" in observation.content
