import shlex
from pathlib import Path

from invoke.tasks import task # type: ignore reportUnknownVariableType
from invoke.context import Context

from functools import wraps
from typing import Callable
from what2 import dbg
from pathlib import Path

__all__ = [
    "pytest",
    "exp",
    "rufff",
    "mk_task",
]

def find_task_dir(ctx: Context):
    cwd = Path(ctx.cwd).absolute()
    dbg(cwd)
    while cwd.parent != cwd:
        tasks = cwd / 'tasks.py'
        if tasks.exists():
            return cwd
        else:
            cwd = cwd.parent


def run(ctx: Context, cmd: list[str]):
    task_dir = find_task_dir(ctx)
    with ctx.cd(task_dir):
        cmd_str = shlex.join(cmd)

        return ctx.run(cmd_str, echo=True, pty=True)


def mk_task(fn: Callable):
    """
    Decorator for a function that returns a shell command as a list of strings and runs them in the invoke context.
    """
    @task
    @wraps(fn)
    def wrapper(ctx: Context, *args, **kwargs):
        cmd = fn(ctx, *args, **kwargs)
        return run(ctx, cmd)
    return wrapper


@mk_task
def pytest(ctx: Context):
    return [
        'pdm',
        'run',
        'python',
        '-m',
        'pytest',
        '-x',
        '-rs'
    ]


@mk_task
def rufff(ctx: Context):
    return [
        'pdm',
        'run',
        'ruff',
        'check',
        str(find_task_dir(ctx)),
        '--fix',
    ]


@mk_task
def py(ctx: Context):
    return [
        'pdm',
        'run',
        'python',
    ]


@mk_task
def exp(ctx: Context):
    return [
        'pdm',
        'run',
        'python',
        'exp.py',
    ]


@mk_task
def atr(ctx: Context):
    return [
        'pdm',
        'run',
        'autodoc2',
        'list',
        './src/what_the_doc',
    ]