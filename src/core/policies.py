# Configuración de Políticas para la POC

# Límites de ejecución
MAX_STEPS = 6  # Máximo de ciclos Decidir -> Ejecutar -> Observar
MAX_TOOL_CALLS = 10
SKILL_TIMEOUT = 30  # segundos
MCP_TIMEOUT = 60    # segundos

# Seguridad
ALLOW_DESTRUCTIVE_ACTIONS = False  # En POC, siempre False
SAFE_MODE = True

# Workspace
WORKSPACE_DIR = "./workspace"
SKILLS_DIR = f"{WORKSPACE_DIR}/skills"
SOUL_FILE = f"{WORKSPACE_DIR}/soul.md"
TOOLS_FILE = f"{WORKSPACE_DIR}/tools.md"
