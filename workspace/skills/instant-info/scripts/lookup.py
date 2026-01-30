import sys
import json
import requests
from bs4 import BeautifulSoup


def search_lite(query):
    try:
        url = "https://lite.duckduckgo.com/lite/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        data = {"q": query}

        response = requests.post(url, data=data, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"summary": "Error al acceder a DuckDuckGo Lite.", "sources": []}

        soup = BeautifulSoup(response.text, "html.parser")

        # En la versión Lite, los resultados están en tablas
        results = []
        sources = []

        # Los links de resultados tienen clase 'result-link'
        links = soup.find_all("a", class_="result-link")
        # Los snippets suelen estar en el siguiente <td> o fila
        snippets = soup.find_all("td", class_="result-snippet")

        for i in range(min(5, len(links))):
            title = links[i].text.strip()
            link = links[i]["href"]
            # Limpiar link de DuckDuckGo redirect si es necesario
            if link.startswith("//duckduckgo.com/l/"):
                # Simplificación para la POC
                link = "https:" + link

            snippet = (
                snippets[i].text.strip() if i < len(snippets) else "Sin descripción."
            )

            results.append(
                f"Result {i + 1}:\nTitle: {title}\nSnippet: {snippet}\nLink: {link}"
            )
            sources.append(link)

        if not results:
            return {
                "summary": f"No se encontraron resultados reales para '{query}' en la web abierta.",
                "sources": [],
            }

        return {"summary": "\n\n".join(results), "sources": sources}

    except Exception as e:
        return {"summary": f"Error de scraping: {str(e)}", "sources": []}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"summary": "Falta la consulta.", "sources": []}))
        sys.exit(0)

    try:
        args = json.loads(sys.argv[1])
        query = args.get("query") or args.get("q")
        if not query:
            print(json.dumps({"summary": "Consulta vacía.", "sources": []}))
        else:
            result = search_lite(query)
            print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"summary": f"Error fatal: {str(e)}", "sources": []}))
