import asyncio
import sys
import os
import shutil
from pathlib import Path

import async_typer
import typer
import microcore as mc
from git import Repo

from .ai_code_review import main
app = async_typer.AsyncTyper()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context):
    if not ctx.invoked_subcommand:
        asyncio.run(main())


@app.async_command(help="Configure LLM for local usage interactively")
async def setup():
    mc.interactive_setup(Path("~/.env.ai-code-review").expanduser())


@app.async_command(help="Review remote code")
async def remote(url=typer.Option(), branch=typer.Option()):
    if os.path.exists("reviewed-repo"):
        shutil.rmtree("reviewed-repo")
    Repo.clone_from(url, branch=branch, to_path="reviewed-repo")
    os.chdir("reviewed-repo")
    await main()
    os.chdir("../")
