from __future__ import annotations

import typing

import nox

SCRIPT_DIRS = ["flare"]


def poetry_session(
    callback: typing.Callable[[nox.Session], None]
) -> typing.Callable[[nox.Session], None]:
    @nox.session(name=callback.__name__)
    def inner(session: nox.Session) -> None:
        session.install("poetry")
        session.run("poetry", "shell")
        session.run("poetry", "install")
        callback(session)

    return inner


def pip_session(
    *args: str, name: str | None = None
) -> typing.Callable[[nox.Session], None]:
    def inner(callback: typing.Callable[[nox.Session], None]):
        @nox.session(name=name or callback.__name__)
        def inner(session: nox.Session):
            for arg in args:
                session.install(arg)
            callback(session)

        return inner

    return inner


@pip_session("black", "isort", "codespell")
def format(session: nox.Session) -> None:
    session.run("black", *SCRIPT_DIRS)
    session.run("isort", *SCRIPT_DIRS)
    session.run("codespell", *SCRIPT_DIRS, "-i", "2")


@pip_session("black", "codespell", "isort")
def lint(session: nox.Session) -> None:
    session.run("black", "--check", *SCRIPT_DIRS)
    session.run("codespell", *SCRIPT_DIRS)
    session.run("isort", "--check", *SCRIPT_DIRS)


@poetry_session
def pyright(session: nox.Session) -> None:
    session.run("poetry", "run", "pyright")


@poetry_session
def pytest(session: nox.Session) -> None:
    session.run("poetry", "run", "pytest", "tests")
