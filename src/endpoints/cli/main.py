import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from src.bootstrap import bootstrap

console = Console()


async def main():
    # 1. Inicializar la aplicación vía Bootstrap
    orchestrator = bootstrap()

    console.print(
        Panel(
            "[bold blue]Agent Skills POC[/bold blue] - Sistema Iniciado",
            subtitle="Arquitectura Clean / Stateless",
            title="Antigravity Agent",
        )
    )
    console.print("[italic]Escribe 'salir' para terminar la sesión.[/italic]\n")

    while True:
        user_input = console.input("[bold green]Usuario:[/bold green] ")

        if user_input.lower() in ["salir", "exit", "quit"]:
            console.print("[yellow]Adiós![/yellow]")
            break

        if not user_input.strip():
            continue

        with console.status(
            "[bold yellow]El agente está razonando...[/bold yellow]", spinner="dots"
        ):
            try:

                async def on_step(step, action):
                    console.print(
                        f"[dim]Step {step}: {action.reason} ({action.type}:{action.name})[/dim]"
                    )

                # Ejecutar el loop agentic
                response = await orchestrator.chat(user_input, on_step_cb=on_step)

                console.print("\n[bold blue]Agente:[/bold blue]")
                console.print(Markdown(response))
                console.print("-" * 40 + "\n")

            except Exception as e:
                console.print(f"[bold red]Error Crítico:[/bold red] {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Proceso interrumpido por el usuario.[/yellow]")
        sys.exit(0)
