import json
import asyncio
import subprocess
from typing import Dict, Any, Optional
from src.core.interfaces.ports import IMCPClient
from src.core.schemas.models import Observation


class MCPStdioClient(IMCPClient):
    """
    Cliente MCP que se comunica con un servidor vía stdio.
    Cumple con el estándar JSON-RPC 2.0 básico definido para la POC.
    """

    def __init__(self, command: str, args: Optional[list[str]] = None):
        self.command = command
        self.args = args or []
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 1

    async def _ensure_connected(self):
        if self.process is None:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    async def call_tool(self, tool_name: str, args: dict) -> Observation:
        try:
            await self._ensure_connected()

            if not self.process or not self.process.stdin or not self.process.stdout:
                return Observation(
                    origin=f"mcp:{tool_name}",
                    content="Error: No se pudo conectar con el servidor MCP.",
                    status="error",
                )

            # Formato JSON-RPC 2.0 simplificado para 'tools/call'
            request = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": args},
            }
            self._request_id += 1

            # Enviar request
            line = json.dumps(request) + "\n"
            self.process.stdin.write(line.encode())
            await self.process.stdin.drain()

            # Leer response
            response_line = await self.process.stdout.readline()

            if not response_line:
                return Observation(
                    origin=f"mcp:{tool_name}",
                    content="Error: Servidor MCP cerró la conexión.",
                    status="error",
                )

            response = json.loads(response_line.decode())

            if "error" in response:
                return Observation(
                    origin=f"mcp:{tool_name}",
                    content=f"Error MCP: {response['error'].get('message')}",
                    status="error",
                )

            # El resultado de un call_tool suele estar en 'result'
            result = response.get("result", {})

            return Observation(
                origin=f"mcp:{tool_name}",
                content=result.get("content", result),  # Manejo de formato variado
                status="success",
            )

        except Exception as e:
            return Observation(
                origin=f"mcp:{tool_name}",
                content=f"Error de conexión MCP: {str(e)}",
                status="error",
            )

    async def stop(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
