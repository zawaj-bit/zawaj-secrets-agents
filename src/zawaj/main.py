"""Point d'entree principal du systeme d'agents Zawaj Secret's."""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from zawaj.agents.orchestrator import OrchestratorAgent
from zawaj.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)

SCHEDULED_TASKS = [
    {
        "id": "post_instagram_matin",
        "cron": {"hour": 9, "minute": 0},
        "task": (
            "Cree et publie un post Instagram pour Zawaj Secret's. "
            "Choisis un theme en rapport avec le mariage islamique. "
            "Redige une legende engageante avec emojis et hashtags. "
            "Utilise le ton de marque : elegant, bienveillant, inspirant."
        ),
    },
    {
        "id": "story_instagram_soir",
        "cron": {"hour": 19, "minute": 0},
        "task": (
            "Cree et publie une story Instagram pour Zawaj Secret's. "
            "Contenu inspirant ou interactif. "
            "Format story vertical, texte court et impactant."
        ),
    },
    {
        "id": "newsletter_hebdo",
        "cron": {"weekday": 1, "hour": 10, "minute": 0},
        "task": (
            "Redige une campagne email Klaviyo hebdomadaire pour Zawaj Secret's. "
            "Sujet : actualites de la boutique, nouvelle collection ou conseil mariage."
        ),
    },
]


async def run_scheduled_task(task_config: dict) -> None:
    """Execute une tache planifiee."""
    task_id = task_config["id"]
    task_text = task_config["task"]
    logger.info("Tache planifiee '%s' demarree", task_id)
    try:
        orchestrator = OrchestratorAgent()
        result = await orchestrator.run(task_text)
        logger.info("Tache '%s' terminee : %s", task_id, result[:120])
        console.print(Panel(result[:500], border_style="green"))
    except Exception as e:
        logger.error("Erreur tache '%s' : %s", task_id, e, exc_info=True)
        console.print(f"[bold red]Erreur tache '{task_id}' : {e}[/bold red]")


async def run_scheduler() -> None:
    """Scheduler leger."""
    import datetime
    console.print("[bold magenta]Scheduler demarre[/bold magenta]")
    executed_today: dict[str, str] = {}
    while True:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        for task in SCHEDULED_TASKS:
            cron = task["cron"]
            task_id = task["id"]
            hour_ok = cron.get("hour", -1) == now.hour
            minute_ok = cron.get("minute", -1) == now.minute
            weekday_ok = ("weekday" not in cron) or (cron["weekday"] == now.weekday())
            if hour_ok and minute_ok and weekday_ok:
                last_run_key = f"{task_id}_{date_str}_{time_str}"
                if executed_today.get(task_id) != last_run_key:
                    executed_today[task_id] = last_run_key
                    asyncio.create_task(run_scheduled_task(task))
        await asyncio.sleep(60)


async def run_interactive() -> None:
    """Mode interactif."""
    orchestrator = OrchestratorAgent()
    while True:
        try:
            request = Prompt.ask("[bold cyan]Votre demande[/bold cyan]")
            if request.lower() in ("exit", "quit", "q", "sortir"):
                console.print("[dim]Au revoir ![/dim]")
                break
            console.print("[dim]Traitement en cours...[/dim]")
            result = await orchestrator.run(request)
            console.print(Panel(result, title="[bold green]Resultat[/bold green]", border_style="green"))
        except KeyboardInterrupt:
            console.print("[dim]Session interrompue.[/dim]")
            break
        except Exception as e:
            logger.error("Erreur lors du traitement", exc_info=True)
            console.print(f"[bold red]Erreur :[/bold red] {e}")


async def run_task(task: str) -> str:
    """Execute une tache unique."""
    orchestrator = OrchestratorAgent()
    return await orchestrator.run(task)


async def run_auto() -> None:
    """Mode automatique."""
    scheduler_task = asyncio.create_task(run_scheduler())
    try:
        await run_interactive()
    finally:
        scheduler_task.cancel()


def main() -> None:
    """Point d'entree CLI."""
    args = sys.argv[1:]
    if "--auto" in args:
        asyncio.run(run_auto())
    elif "--scheduler" in args:
        console.print("[bold yellow]Mode serveur : scheduler seul[/bold yellow]")
        asyncio.run(run_scheduler())
    elif args:
        task = " ".join(a for a in args if not a.startswith("--"))
        result = asyncio.run(run_task(task))
        console.print(result)
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
