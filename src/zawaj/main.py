"""Point d'entrée principal du système d'agents Zawaj Secret's."""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from zawaj.agents.orchestrator import OrchestratorAgent
from zawaj.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


async def run_interactive() -> None:
    """Mode interactif — l'utilisateur saisit des demandes."""
    console.print(Panel.fit(
        "[bold magenta]✨ Zawaj Secret's — Agents IA[/bold magenta]\n"
        "[dim]Automatisation Instagram · Klaviyo · Canva[/dim]",
        border_style="magenta",
    ))

    orchestrator = OrchestratorAgent()

    console.print("\n[bold]Exemples de demandes :[/bold]")
    console.print("  • Créer un post Instagram pour la collection Ramadan")
    console.print("  • Préparer une campagne email Klaviyo pour le lancement d'un produit")
    console.print("  • Générer un visuel Canva pour les stories du week-end")
    console.print("  • Planifier une campagne complète pour l'Aïd El-Fitr\n")

    while True:
        try:
            request = Prompt.ask("[bold cyan]Votre demande[/bold cyan]")
            if request.lower() in ("exit", "quit", "q", "sortir"):
                console.print("\n[dim]Au revoir ! ✨[/dim]")
                break

            console.print("\n[dim]Traitement en cours...[/dim]\n")
            result = await orchestrator.run(request)
            console.print(Panel(result, title="[bold green]Résultat[/bold green]", border_style="green"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[dim]Session interrompue.[/dim]")
            break
        except Exception as e:
            logger.error("Erreur lors du traitement", exc_info=True)
            console.print(f"[bold red]Erreur :[/bold red] {e}")


async def run_task(task: str) -> str:
    """Exécute une tâche unique et retourne le résultat."""
    orchestrator = OrchestratorAgent()
    return await orchestrator.run(task)


def main() -> None:
    """Point d'entrée CLI."""
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        result = asyncio.run(run_task(task))
        console.print(result)
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
