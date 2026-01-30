import sys
import json


def handle_request(request):
    try:
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "resolve-library-id":
                lib_name = arguments.get("libraryName", "").lower()
                if "pydantic" in lib_name:
                    result = {
                        "libraryId": "/pydantic/pydantic",
                        "message": "Encontrado exacto.",
                    }
                elif "react" in lib_name:
                    result = {
                        "libraryId": "/facebook/react",
                        "message": "Encontrado exacto.",
                    }
                else:
                    result = {
                        "libraryId": f"/mock/{lib_name}",
                        "message": "ID generado (simulado).",
                    }

                return {"result": result}

            elif tool_name == "query-docs":
                lib_id = arguments.get("libraryId", "")
                query = arguments.get("query", "")

                content = f"Documentación simulada para {lib_id} sobre '{query}':\n\n1. Use standard patterns.\n2. Follow Clean Architecture.\n3. Documentation coverage is high."
                return {"result": {"content": content}}

            else:
                return {
                    "error": {
                        "message": f"Tool '{tool_name}' no encontrada en el bridge."
                    }
                }

        else:
            return {"error": {"message": f"Método '{method}' no soportado."}}

    except Exception as e:
        return {"error": {"message": str(e)}}


if __name__ == "__main__":
    # Bucle infinito para leer JSON-RPC desde stdin
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        try:
            request = json.loads(line)
            response = handle_request(request)
            response["jsonrpc"] = "2.0"
            response["id"] = request.get("id")

            print(json.dumps(response), flush=True)
        except Exception:
            pass
