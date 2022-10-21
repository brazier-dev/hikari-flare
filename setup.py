import os
import re
import types

from setuptools import find_namespace_packages, setup

name = "flare"


def parse_meta() -> types.SimpleNamespace:
    with open(os.path.join(name, "__init__.py")) as fp:
        code = fp.read()

    token_pattern = re.compile(r"^__(?P<key>\w+)?__\s*=\s*(?P<quote>(?:'{3}|\"{3}|'|\"))(?P<value>.*?)(?P=quote)", re.M)

    groups = {}

    for match in token_pattern.finditer(code):
        group = match.groupdict()
        groups[group["key"]] = group["value"]

    return types.SimpleNamespace(**groups)


def long_description() -> str:
    with open("README.md") as fp:
        return fp.read()


def parse_requirements_file(path: str) -> list[str]:
    with open(path) as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]


meta = parse_meta()

setup(
    name="hikari-flare",
    version=meta.version,
    description="Stateless component manager for hikari with type-safe API.",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="Lunarmagpie",
    author_email="bambolambo0@gmail.com",
    url="https://github.com/Lunarmagpie/hikari-flare",
    packages=find_namespace_packages(include=[name + "*"]),
    package_data={"flare": ["py.typed"]},
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_requirements_file("requirements.txt"),
    extras_require={
        "dev": parse_requirements_file("dev_requirements.txt"),
    },
    python_requires=">=3.10.0,<3.12",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)