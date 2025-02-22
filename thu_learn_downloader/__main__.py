import sys
from pathlib import Path

import typer
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from . import sync
from .config import Config
from .constants import MAX_ACTIVE_TASKS, SUCCESS_PREFIX
from .downloader import Downloader
from .helper import Helper

app = typer.Typer(name="tld")


@app.command(name="tld")
def main(
    username: str = typer.Option("liqin20", "-u", "--username"),
    password: str = typer.Option(
        None, "-p", "--password", prompt=True, hide_input=True
    ),
    semester: list[str] = typer.Option(["2022-2023-2"], "-s", "--semester"),
    course: list[str] = typer.Option([], "-c", "--course"),
    prefix: Path = typer.Option(Path.home() / "Desktop" / "thu-learn", "--prefix"),
    size_limit: int = typer.Option(sys.maxsize, "-s", "--size-limit"),
) -> None:
    config = Config(
        username=username,
        password=password,
        semesters=semester,
        courses=course,
        prefix=prefix,
        size_limit=size_limit,
    )
    helper = Helper()
    downloader = Downloader()
    overall_progress = Progress(
        TextColumn("{task.description}", style="bold bright_blue"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )
    semesters_task_id = overall_progress.add_task(description="Semesters")
    courses_task_id = overall_progress.add_task(description="Courses")
    progress_group = Group(
        Panel(downloader.progress, height=MAX_ACTIVE_TASKS + 2),
        Panel(overall_progress),
    )

    with Live(progress_group) as live:
        with downloader.pool:
            try:
                helper.login(username=username, password=password)
            except:
                live.console.log(
                    f"Login as {username} FAILED",
                    style="bold bright_red",
                )
            else:
                live.console.log(
                    SUCCESS_PREFIX,
                    f"Login as {username} SUCCESS",
                    style="bold bright_green",
                )
                sync.sync_all(
                    helper=helper,
                    downloader=downloader,
                    config=config,
                    console=live.console,
                    overall_progress=overall_progress,
                    semesters_task_id=semesters_task_id,
                    courses_task_id=courses_task_id,
                )


if __name__ == "__main__":
    app()
