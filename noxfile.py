from __future__ import annotations

import typing

import nox

SCRIPT_DIRS = ["flare"]


def pip_session(*args: str, name: str | None = None) -> typing.Callable[[nox.Session], None]:
    def inner(callback: typing.Callable[[nox.Session], None]):
        @nox.session(name=name or callback.__name__)
        def inner(session: nox.Session) -> None:
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


@pip_session("black", "isort", "codespell")
def lint(session: nox.Session) -> None:
    session.run("black", "--check", *SCRIPT_DIRS)
    session.run("codespell", *SCRIPT_DIRS)
    session.run("isort", "--check", *SCRIPT_DIRS)


@pip_session(".", "pyright")
def pyright(session: nox.Session) -> None:
    session.run("pyright", *SCRIPT_DIRS)


@pip_session(".", "pytest")
def pytest(session: nox.Session) -> None:
    session.run("pytest", "tests")
