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

# ─── Tâches automatiques planifiées ──────────────────────────────────────────
# Modifie ces tâches selon tes besoins. Le scheduler les exécute automatiquement.
SCHEDULED_TASKS = [
        {
                    "id": "post_instagram_matin",
                    "cron": {"hour": 9, "minute": 0},   # Tous les jours à 9h00
                    "task": (
                                    "Crée et publie un post Instagram pour Zawaj Secret's. "
                                    "Choisis un thème en rapport avec le mariage islamique, la modestie ou nos collections. "
                                    "Rédige une légende engageante avec emojis et hashtags. "
                                    "Utilise le ton de marque : élégant, bienveillant, inspirant."
                    ),
        },
        {
                    "id": "story_instagram_soir",
                    "cron": {"hour": 19, "minute": 0},  # Tous les jours à 19h00
                    "task": (
                                    "Crée et publie une story Instagram pour Zawaj Secret's. "
                                    "Contenu inspirant ou interactif (sondage, question, citation). "
                                    "Format story vertical, texte court et impactant."
                    ),
        },
        {
                    "id": "newsletter_hebdo",
                    "cron": {"weekday": 1, "hour": 10, "minute": 0},  # Chaque lundi à 10h
                    "task": (
                                    "Rédige et prépare une campagne email Klaviyo hebdomadaire pour Zawaj Secret's. "
                                    "Sujet : actualités de la boutique, nouvelle collection ou conseil mariage. "
                                    "Segment : toute la liste. Objet de l'email accrocheur, contenu chaleureux et élégant."
                    ),
        },
]
# ─────────────────────────────────────────────────────────────────────────────


async def run_scheduled_task(task_config: dict) -> None:
        """Exécute une tâche planifiée."""
        task_id = task_config["id"]
        task_text = task_config["task"]
        logger.info("⏰ Tâche planifiée '%s' démarrée", task_id)
        try:
                    orchestrator = OrchestratorAgent()
                    result = await orchestrator.run(task_text)
                    logger.info("✅ Tâche '%s' terminée : %s", task_id, result[:120])
                    console.print(f"\n[bold green]✅ Tâche automatique '{task_id}' terminée[/bold green]")
                    console.print(Panel(result[:500], border_style="green"))
except Exception as e:
        logger.error("❌ Erreur tâche '%s' : %s", task_id, e, exc_info=True)
        console.print(f"[bold red]❌ Erreur tâche '{task_id}' : {e}[/bold red]")


async def run_scheduler() -> None:
        """Scheduler léger — vérifie toutes les minutes si une tâche doit tourner."""
        import datetime
        console.print("[bold magenta]⏰ Scheduler démarré — vérification toutes les minutes[/bold magenta]")
        executed_today: dict[str, str] = {}  # task_id → date d'exécution

    while True:
                now = datetime.datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M")

        for task in SCHEDULED_TASKS:
                        cron = task["cron"]
                        task_id = task["id"]

            # Calcule si c'est l'heure d'exécution
                        hour_ok = cron.get("hour", -1) == now.hour
                        minute_ok = cron.get("minute", -1) == now.minute
                        weekday_ok = ("weekday" not in cron) or (cron["weekday"] == now.weekday())

            if hour_ok and minute_ok and weekday_ok:
                                # Évite de re-lancer deux fois dans la même minute
                                last_run_key = f"{task_id}_{date_str}_{time_str}"
                                if executed_today.get(task_id) != last_run_key:
                                                        executed_today[task_id] = last_run_key
                                                        asyncio.create_task(run_scheduled_task(task))

                        await asyncio.sleep(60)  # attend 1 minute


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


async def run_auto() -> None:
        """Mode automatique : scheduler + mode interactif en parallèle."""
        console.print(Panel.fit(
            "[bold magenta]✨ Zawaj Secret's — Mode Automatique[/bold magenta]\n"
            "[dim]Scheduler actif + interface interactive[/dim]",
            border_style="magenta",
        ))
        # Lance le scheduler en arrière-plan ET l'interface interactive
        scheduler_task = asyncio.create_task(run_scheduler())
    try:
                await run_interactive()
finally:
            scheduler_task.cancel()


def main() -> None:
        """Point d'entrée CLI.

            Utilisation :
                  python -m zawaj.main              # Mode interactif simple
                        python -m zawaj.main --auto       # Mode automatique (scheduler + interactif)
                              python -m zawaj.main --scheduler  # Scheduler seul (pour serveur)
                                    python -m zawaj.main "ma tâche"   # Tâche unique en ligne de commande
                                        """
        args = sys.argv[1:]

    if "--auto" in args:
                asyncio.run(run_auto())
elif "--scheduler" in args:
            console.print("[bold yellow]🤖 Mode serveur : scheduler seul[/bold yellow]")
            asyncio.run(run_scheduler())
elif args:
            task = " ".join(a for a in args if not a.startswith("--"))
            result = asyncio.run(run_task(task))
            console.print(result)
else:
            asyncio.run(run_interactive())


if __name__ == "__main__":
        main()
    
